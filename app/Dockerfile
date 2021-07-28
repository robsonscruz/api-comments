FROM python:3.8-slim-buster
RUN apt-get update
RUN apt-get install stress-ng -y
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install -r requirements.txt
COPY . .
EXPOSE 80
CMD ["gunicorn", "--workers=3", "--bind", "0.0.0.0:80", "api:app"]