from app import app
from models import db, User

with app.app_context():
    db.create_all()

    if not User.query.filter_by(role='Admin').first():
        admin = User(username='admin', email='admin@team.com', role='Admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

    print("Database created successfully")