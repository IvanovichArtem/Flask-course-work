FROM python:3.9

WORKDIR /app
COPY requirements.txt /app
RUN pip install --upgrade pip &&  python -m pip install -r requirements.txt

COPY . /app

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
