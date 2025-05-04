docker-compose down -v
docker-compose up -d --build
docker-compose exec backend python manage.py migrate
docker-compose logs -f celery
docker-compose ps