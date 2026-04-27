# myservices
A-Z Services — Book trusted home services at your doorstep. From cleaning to repairs, we've got you covered.

## Tech Stack
- **Backend:** Python, Flask, Flask-SQLAlchemy
- **Database:** SQLite
- **Frontend:** Jinja2 Templates, HTML/CSS
- **Charts:** Matplotlib

## Project Structure
```
myservices/
├── app.py               # App factory & entry point
├── backend/
│   ├── models.py        # Database models
│   ├── admin.py         # Admin routes
│   ├── customer.py      # Customer routes
│   ├── professional.py  # Professional routes
│   └── redirect.py      # Redirect/auth routes
├── templates/
│   ├── admin/
│   ├── customer/
│   ├── professional/
│   ├── layout.html
│   ├── login.html
│   └── signup.html
├── static/resumes/      # Uploaded professional documents
├── instance/            # SQLite database
└── requirements.txt
```

## Roles
- **Admin** — Manage services, packages, verify professionals, view summary
- **Customer** — Browse services, book requests, rate professionals
- **Professional** — View assigned requests, manage profile, upload resume

## Setup & Run

```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

App runs at `http://127.0.0.1:5000`


