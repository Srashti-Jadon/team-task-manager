from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Project, Task
from config import Config
from datetime import datetime, date
from functools import wraps
import os

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
with app.app_context():
    db.create_all()

@app.route("/")
def index():
    if 'user_id' in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route('/create-admin')
def create_admin():
    user = User.query.filter_by(email="admin@gmail.com").first()

    if not user:
        admin = User(
            username="admin",
            email="admin@gmail.com",
            role="Admin"
        )
        admin.set_password("admin123")

        db.session.add(admin)
        db.session.commit()

        return "Admin created successfully"

    return "Admin already exists"

# =============================================================================
# CREATE TABLES (SAFE FOR LOCAL + DEPLOY)
# =============================================================================
#with app.app_context():
 #   db.create_all()

# =============================================================================
# LOGIN HELPERS
# =============================================================================

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrap


def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))

        user = db.session.get(User, session['user_id'])
        if not user or not user.is_admin():
            return redirect(url_for('dashboard'))

        return f(*args, **kwargs)
    return wrap


# =============================================================================
# AUTH ROUTES
# =============================================================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        # 🔒 Force role = Member ONLY
        role = "Member"

        # check duplicate email
        if User.query.filter_by(email=email).first():
            flash("Email already registered. Please login.", "error")
            return redirect(url_for("register"))

        # check duplicate username
        if User.query.filter_by(username=username).first():
            flash("Username already taken.", "error")
            return redirect(url_for("register"))

        user = User(
            username=username,
            email=email,
            role=role
        )

        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()

        if user and user.check_password(request.form['password']):
            session['user_id'] = user.id
            session['role'] = user.role
            return redirect(url_for('dashboard'))

        return redirect(url_for('login'))

    return render_template("login.html")


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# =============================================================================
# DASHBOARD
# =============================================================================

@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    user = db.session.get(User, session.get('user_id'))

    if not user:
        session.clear()
        return redirect(url_for('login'))

    tasks = Task.query.filter_by(assigned_to_id=user.id)

    total = tasks.count()
    completed = tasks.filter_by(status='Done').count()
    pending = tasks.filter_by(status='Pending').count()

    overdue = Task.query.filter(
        Task.assigned_to_id == user.id,
        Task.status != 'Done',
        Task.due_date < date.today()
    ).count()

    return render_template(
        "dashboard.html",
        total=total,
        completed=completed,
        pending=pending,
        overdue=overdue,
        user=user
    )


# =============================================================================
# PROJECTS
# =============================================================================

@app.route('/projects')
@login_required
def projects():
    user = db.session.get(User, session['user_id'])

    if user.is_admin():
        projects = Project.query.all()
    else:
        projects = Project.query.filter_by(user_id=user.id).all()

    return render_template("projects.html", projects=projects)


@app.route('/project/create', methods=['GET', 'POST'])
@admin_required
def create_project():
    if request.method == 'POST':
        project = Project(
            name=request.form['name'],
            description=request.form['description'],
            user_id=session['user_id']
        )

        db.session.add(project)
        db.session.commit()

        return redirect(url_for('projects'))

    return render_template("project_form.html")


@app.route('/project/<int:project_id>')
@login_required
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    user = db.session.get(User, session['user_id'])

    if not user.is_admin() and project.user_id != user.id:
        return redirect(url_for('projects'))

    tasks = Task.query.filter_by(project_id=project_id).all()

    return render_template(
        "project_detail.html",
        project=project,
        tasks=tasks,
        current_date=date.today(),
        user=user
    )


@app.route('/project/<int:project_id>/task/new', methods=['GET', 'POST'])
@admin_required
def create_task(project_id):
    project = Project.query.get_or_404(project_id)
    users = User.query.all()

    if request.method == 'POST':
        task = Task(
            title=request.form['title'],
            description=request.form['description'],
            assigned_to_id=int(request.form['assigned_to_id']),
            status=request.form['status'],
            due_date=datetime.strptime(request.form['due_date'], '%Y-%m-%d').date(),
            project_id=project.id
        )

        db.session.add(task)
        db.session.commit()

        return redirect(url_for('project_detail', project_id=project.id))

    return render_template('task_form.html', project=project, users=users)


# =============================================================================
# TASKS
# =============================================================================

@app.route('/tasks')
@login_required
def my_tasks():
    user = db.session.get(User, session['user_id'])
    tasks = Task.query.filter_by(assigned_to_id=user.id).all()

    return render_template("tasks.html", tasks=tasks, current_date=date.today())


@app.route('/task/<int:task_id>/update', methods=['POST'])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    user = db.session.get(User, session['user_id'])

    if task.assigned_to_id != user.id and not user.is_admin():
        return redirect(url_for('my_tasks'))

    task.status = request.form['status']
    db.session.commit()

    return redirect(url_for('my_tasks'))


# =============================================================================
# TEST
# =============================================================================

@app.route('/test')
def test():
    return "App is working"


# =============================================================================
# RUN
# =============================================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)