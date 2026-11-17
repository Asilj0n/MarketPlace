# Django Food App

A simple Django web app for browsing and managing food menu items. Users can register, log in, and add their own dishes with a name, description, price, and image.

## Features

- **Food catalog** — list and detail pages for menu items
- **Add / edit / delete items** — create items linked to the logged-in user
- **User accounts** — register, login, logout, and profile page
- **Profiles** — each user gets a profile (via Django signals) with image and location
- **Auth protection** — adding items requires login
- **Bootstrap UI** — styled templates for food and auth pages

## Project structure

```text
mysite/          # project settings and main URLs
food/            # food items (models, views, templates)
users/           # accounts, profiles, signals
```

## Tech stack

- Python
- Django 4.2
- Bootstrap 5
- SQLite (default database)

## Getting started

### 1. Clone the repo

```bash
git clone https://github.com/Asilj0n/django_food_app.git
cd django_food_app
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
```

**Windows:**

```bash
venv\Scripts\activate
```

**macOS / Linux:**

```bash
source venv/bin/activate
```

### 3. Install Django

```bash
pip install django pillow
```

(`pillow` is needed for profile image fields.)

### 4. Run migrations

```bash
python manage.py migrate
```

### 5. Create a superuser (optional, for admin)

```bash
python manage.py createsuperuser
```

### 6. Start the server

```bash
python manage.py runserver
```

Open [http://127.0.0.1:8000/food/](http://127.0.0.1:8000/food/) in your browser.

## Main URLs

| URL | Description |
|-----|-------------|
| `/food/` | Food item list |
| `/food/add/` | Add a new item (login required) |
| `/food/<id>/` | Item detail |
| `/register/` | Create an account |
| `/login/` | Log in |
| `/logout/` | Log out |
| `/profile/` | User profile |
| `/admin/` | Django admin |

## Notes for learning

This project practices common Django ideas:

- function-based and class-based views (`ListView`, `DetailView`, `CreateView`)
- models and foreign keys (`Item` → `User`)
- Django signals (auto-create `Profile` when a `User` is created)
- authentication (`LoginView`, `LogoutView`, `LoginRequiredMixin`)
- forms and template rendering with Bootstrap

## License

Personal / educational project.
