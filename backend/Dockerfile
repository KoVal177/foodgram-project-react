FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r ./requirements.txt --no-cache-dir

COPY ../ ./

RUN python manage.py makemigrations

CMD ["gunicorn", "backend.wsgi:application", "--bind", "0:8000" ]
