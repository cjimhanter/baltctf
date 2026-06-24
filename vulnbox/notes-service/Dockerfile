FROM python:3.12-slim

WORKDIR /app

COPY app.py /app/app.py

RUN pip install --no-cache-dir flask==3.1.0

# Уязвимое состояние по умолчанию: отладочный режим включён, IDOR-фикс выключен.
ENV NOTES_DEBUG=1 \
    NOTES_SECURE=0 \
    NOTES_DB_PATH=/app/notes.db \
    NOTES_HOST=0.0.0.0 \
    NOTES_PORT=8080

EXPOSE 8080

CMD ["python", "app.py"]
