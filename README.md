# MarketPlace

A campus marketplace for University of Central Asia students. Students list things they want to sell or give away (textbooks, electronics, dorm furniture, clothes and more), other students browse and message the seller on WhatsApp, and they meet on campus to make the deal. There is no online payment.

Only people with an `@ucentralasia.org` email address can sign up.

## Features

- **University-only accounts.** Registration accepts only `@ucentralasia.org` emails. New accounts stay inactive until the student clicks the activation link sent to that address.
- **Listings.** Title, description, category, condition, price (0 = free), campus and one photo.
- **Status.** Each listing is *available*, *reserved* or *sold*. Only the seller can change it.
- **Browse and search.** Search by keyword and filter by category, campus or free items. Sold items are hidden unless you ask for them. Results are paginated.
- **Contact by WhatsApp.** Every student adds a WhatsApp number. Listings show a "Message seller on WhatsApp" button with a ready-made message.
- **Ownership.** Only the seller can edit, delete or change the status of a listing.
- **Profile page.** Edit campus, WhatsApp number and photo, and see all your listings.
- **Login required.** Every page except login and sign-up needs an account.

## Project structure

```text
mysite/          # settings, root URLs, shared form helpers
listings/        # the Listing model, browse/detail/create/edit/delete views
users/           # registration, email activation, profiles
templates/       # base layout and shared form template
static/css/      # site styles
```

## Getting started

```bash
git clone https://github.com/Asilj0n/MarketPlace.git
cd MarketPlace
python -m venv venv
venv\Scripts\activate            # Windows
# source venv/bin/activate       # macOS / Linux
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser # optional, for /admin/
python manage.py runserver
```

Open <http://127.0.0.1:8000/>.

### Activating accounts in development

In development, emails are **printed in the terminal** running `runserver` instead of being sent. After signing up, copy the activation link from the terminal and open it in your browser.

To send real emails, set these environment variables before starting the server:

```text
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
DEFAULT_FROM_EMAIL=MarketPlace <noreply@example.com>
```

You can also activate a user by hand in `/admin/` by ticking **Active**.

## Main URLs

| URL | Description |
|-----|-------------|
| `/` | Browse listings |
| `/new/` | Post a listing |
| `/<id>/` | Listing details |
| `/<id>/edit/` | Edit your listing |
| `/<id>/delete/` | Delete your listing |
| `/register/` | Sign up with a university email |
| `/activate/<uid>/<token>/` | Activation link from the email |
| `/login/`, `/logout/` | Log in / log out |
| `/profile/` | Your profile and your listings |
| `/admin/` | Django admin |

## Settings you may want to change

In `mysite/settings.py`:

- `ALLOWED_EMAIL_DOMAIN`: the email domain allowed to register (default `ucentralasia.org`).
- `MAX_UPLOAD_SIZE_MB`: the largest photo upload allowed (default 5).

Campuses and their currencies are defined in `users/models.py` (`Campus`, `CAMPUS_CURRENCY`). Listing categories are defined in `listings/models.py`.

## Running tests

```bash
python manage.py test
```

## History

This project started as the final project of our Django course: a food menu app. It was later rebuilt into a campus marketplace.
