FROM python:3.12-slim

WORKDIR /app

COPY app.py /app/app.py

RUN pip install --no-cache-dir flask==3.1.0

CMD ["python", "app.py"]

