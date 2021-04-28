release: python manage.py collectstatic --noinput && python manage.py migrate
web: gunicorn wewager_next.wsgi --reload --workers=2 --threads=4 --worker-tmp-dir=/dev/shm --bind=0.0.0.0:8080 --log-file=- --worker-class=gthread
worker: python manage.py runapscheduler