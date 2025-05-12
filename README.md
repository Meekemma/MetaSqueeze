Got it! You want a **full README.md** that guides the user step-by-step on **how to set up MetaSqueeze from scratch**, including:

* Cloning repo
* Creating & configuring `.env`
* Installing dependencies (if needed)
* Generating Django SECRET\_KEY
* Running migrations
* Starting services (Docker & Celery)
* Accessing Swagger UI

Here's the **corrected & complete README.md** for you, in Markdown:

---

````markdown
# 🗜️ MetaSqueeze

MetaSqueeze is a backend service for **document conversion** and **image optimization**. It allows conversion between **PDF, DOCX, TXT** formats, and image optimization (resize, compress, format conversion) across **PNG, JPEG, WEBP**. Powered by **Django**, **DRF**, **Celery**, **Redis**, and **Docker**.

---

## 🚀 Features

- Image optimization & format conversion (PNG, JPEG, WEBP)
- Document conversion (PDF ⇄ DOCX, PDF/DOCX ⇄ TXT)
- Asynchronous background processing (Celery + Redis)
- Scheduled tasks for cleanup & optimization
- User authentication with email verification
- File size limit enforcement & rate limiting
- Expiring download links & task progress tracking
- Dockerized deployment for easy setup
- API Documentation via Swagger

---

## 🛠️ Tech Stack

- Django, Django REST Framework
- Celery + Redis (Task Queue)
- PostgreSQL (Database)
- Docker & Docker Compose
- Celery Beat (Scheduled Tasks)
- Django Admin & Logging

---

## 📦 Installation & Setup

### 1️⃣ Clone the repository

```bash
git clone https://github.com/Meekemma/MetaSqueeze.git
cd MetaSqueeze
````

---

### 2️⃣ Create a `.env` file

Duplicate the `.env.example` provided:

```bash
cp .env.example .env
```

Edit the `.env` file with your configurations:

* `DJANGO_SECRET_KEY`: Generate using the command below.
* `DEBUG=1` for development.
* Update `POSTGRES_*` credentials if needed.

---

### 3️⃣ Generate Django SECRET\_KEY

Run this command to generate a secret key:

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Copy the key and paste it into your `.env`:

```env
DJANGO_SECRET_KEY=your-generated-secret-key
```

---

### 4️⃣ Build & Start Docker Containers

```bash
docker-compose up --build
```

This will start:

* Django API on `http://localhost:8000`
* PostgreSQL Database
* Redis Broker
* Celery Worker
* Celery Beat (Scheduler)

---

### 5️⃣ Run Migrations & Create Superuser

In a new terminal:

```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

Follow prompts to create your admin account.

---

### 6️⃣ Access the App

* **API Docs (Swagger UI):** [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
* **Django Admin Panel:** [http://localhost:8000/admin/](http://localhost:8000/admin/)

---

## ⚙️ Running Celery (Manually for Dev)

For development without Docker Compose:

```bash
celery -A metasqueeze worker --loglevel=info
celery -A metasqueeze beat --loglevel=info
```

---

## 🕒 Scheduled Tasks

* Cleanup expired downloads (every 6 hours)
* Auto-optimize storage files (daily)
* Health check tasks

---

## 🧪 Running Tests

```bash
docker-compose exec web python manage.py test
```

---

## 🛡️ Security Features

* File size restrictions.
* MIME type & format validation.
* API rate limiting & user throttling.
* Secure token-based email verification.
* Expiring download links for files.

---

## 📊 Roadmap

* ✅ Image & Document Conversion
* ✅ Celery Integration for Async Tasks
* ✅ Dockerized Deployment
* ✅ Scheduled Maintenance Tasks
* ✅ User Authentication & Security
* ✅ Progress Tracking & History
* ✅ Swagger API Documentation




## 🔗 Useful Commands Recap

| Command                                                    | Purpose             |
| ---------------------------------------------------------- | ------------------- |
| `docker-compose up --build`                                | Start the app stack |
| `docker-compose exec web python manage.py migrate`         | Run DB migrations   |
| `docker-compose exec web python manage.py createsuperuser` | Create admin user   |
| `celery -A metasqueeze worker --loglevel=info`             | Run Celery worker   |
| `celery -A metasqueeze beat --loglevel=info`               | Run periodic tasks  |
| `docker-compose exec web python manage.py test`            | Run tests           |

```

---

## ✨ Author

Made with ❤️ by [Meekemma](https://github.com/Meekemma)

---

---

## 📝 License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

