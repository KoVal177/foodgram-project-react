FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r ./requirements.txt --no-cache-dir

COPY ../ ./

RUN python manage.py makemigrations
#RUN python manage.py migrate
#RUN python manage.py load_initial_data


#CMD ["python3", "manage.py", "runserver", "0:8000" ]
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0:8000" ]
