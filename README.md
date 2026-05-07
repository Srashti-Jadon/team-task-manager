TEAM TASK MANAGER

DESCRIPTION:
This is a full-stack web application built using Flask and PostgreSQL.
It allows users to manage projects, assign tasks, and track progress with role-based access control (Admin and Member).

FEATURES:
- User Registration and Login system
- Role-based access (Admin / Member)
- Create and manage Projects
- Create, assign, and update Tasks
- Dashboard showing task statistics (completed, pending, overdue)
- PostgreSQL database integration
- Session-based authentication

TECH STACK:
- Backend: Flask (Python)
- Database: PostgreSQL (Railway)
- Frontend: HTML, CSS, Bootstrap
- Deployment: Railway

ROLES:
Admin:
- Create projects
- Assign tasks to users
- Manage all tasks and projects

Member:
- View assigned tasks
- Update task status

DATABASE:
- PostgreSQL hosted on Railway
- Tables: User, Project, Task

SETUP:
1. Install dependencies using requirements.txt
2. Set DATABASE_URL in environment variables
3. Run app.py
4. Access /login to start

AUTHOR:
Srashti Jadon
