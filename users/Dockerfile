FROM python:3.9

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
ENV USERS_URL default
ENV DATABASE_URL postgresql://admin:admin@34.135.18.78/terminus_db
COPY . .

CMD ["gunicorn","--reload", "wsgi:app", "--bind", "0.0.0.0:3000", "--log-level", "debug"]
