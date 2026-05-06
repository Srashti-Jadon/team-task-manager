from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Project, Task
from config import Config
from datetime import datetime, date
import os

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# =============================================================================
# LOGIN HELPERS
# =============================================================================

def login_required(f):
    def wrap(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap


def admin_required(f):
    def wrap(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first', 'warning')
            return redirect(url_for('login'))

        user = User.query.get(session['user_id'])
        if not user or not user.is_admin():
            flash('Admin access required', 'error')
            return redirect(url_for('dashboard'))

        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap


# =============================================================================
# ROUTES
# =============================================================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role', 'Member')

        if User.query.filter_by(username=username).first():
            flash("Username already exists", "error")
            return redirect(url_for('register'))

        user = User(username=username, email=email, role=role)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash("Registered successfully", "success")
        return redirect(url_for('login'))

    return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            return redirect(url_for('dashboard'))

        flash("Invalid credentials", "error")

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
    user = User.query.get(session['user_id'])

    total = Task.query.filter_by(assigned_to_id=user.id).count()
    completed = Task.query.filter_by(assigned_to_id=user.id, status='Done').count()
    pending = Task.query.filter_by(assigned_to_id=user.id, status='Pending').count()

    overdue = Task.query.filter(
        Task.assigned_to_id == user.id,
        Task.status != 'Done',
        Task.due_date < date.today()
    ).count()

    return render_template("dashboard.html",
                           total=total,
                           completed=completed,
                           pending=pending,
                           overdue=overdue,
                           user=user)


# =============================================================================
# PROJECTS
# =============================================================================

@app.route('/projects')
@login_required
def projects():
    user = User.query.get(session['user_id'])

    if user.is_admin():
        projects = Project.query.all()
    else:
        projects = Project.query.filter_by(user_id=user.id).all()

    return render_template("projects.html", projects=projects)


@app.route('/project/create', methods=['GET', 'POST'])
@admin_required
def create_project():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']

        project = Project(name=name, description=description, user_id=session['user_id'])
        db.session.add(project)
        db.session.commit()

        return redirect(url_for('projects'))

    return render_template("project_form.html")


@app.route('/project/<int:project_id>')
@login_required
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)

    tasks = Task.query.filter(Task.project_id == project_id).all()

    user = User.query.get(session['user_id'])

    # permission check (important)
    if not user.is_admin() and project.user_id != user.id:
        flash("Access denied", "error")
        return redirect(url_for('projects'))

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

    users = User.query.all()   # MUST be here for GET

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        assigned_to_id = request.form['assigned_to_id']
        status = request.form['status']
        due_date_str = request.form['due_date']

        if not title or not assigned_to_id or not due_date_str:
            flash("Missing fields", "error")
            return render_template('task_form.html', project=project, users=users)

        due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()

        task = Task(
            title=title,
            description=description,
            assigned_to_id=int(assigned_to_id),
            status=status,
            due_date=due_date,
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
    user = User.query.get(session['user_id'])
    tasks = Task.query.filter_by(assigned_to_id=user.id).all()

    return render_template(
        "tasks.html",
        tasks=tasks,
        current_date=date.today()
    )


@app.route('/task/<int:task_id>/update', methods=['POST'])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    user = User.query.get(session['user_id'])

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
# RUN (ONLY FOR LOCAL)
# =============================================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)