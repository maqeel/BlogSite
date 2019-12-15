FROM python:3.6-slim

RUN pip install psycopg2-binary Flask Flask-Bcrypt Flask-Login Flask-SQLAlchemy Flask-WTF WTForms

COPY register.py /register.py
COPY static /static
COPY templates /templates
WORKDIR /

CMD ["register.py"]