# SkillLink

Share What You Know, Learn What You Need. A web platform where students list skills they can teach and want to learn, then connect with each other.

**Phase 1: Account Feature** (registration, login/logout, role-based dashboards, user profile)

## Tech stack
- Django (templates for the frontend)
- PostgreSQL / Supabase

## Setup
```bash
git clone <your-repo-url>
cd <repo-folder>
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
```


1. Copy `.env.example` to `.env` and fill in your database details (and a SECRET_KEY).
2. Make sure the PostgreSQL database in `DB_NAME` exists (or use your Supabase connection details and set `DB_SSLMODE=require`).
3. Run:
```bash
python manage.py migrate
python manage.py createsuperuser   # this account gets the Admin role
python manage.py runserver
```
Open http://127.0.0.1:8000/
python manage.py runserver 8080

## Roles
| Role | How you get it | Dashboard |
|------|----------------|-----------|
| Student | Registration form | `/dashboard/student/` |
| Admin | `createsuperuser` | `/dashboard/admin/` |

A student cannot open the admin dashboard and an admin cannot open the student dashboard, even by typing the URL.

## Pages
| URL | Page |
|-----|------|
| `/register/` | Register |
| `/login/` | Log in |
| `/dashboard/` | Redirects to your role's dashboard |
| `/profile/` | View your profile |
| `/profile/edit/` | Edit your profile |

## Run the tests
```bash
python manage.py test accounts
```
(Django creates a temporary test database, so your database user needs permission to create databases.)
