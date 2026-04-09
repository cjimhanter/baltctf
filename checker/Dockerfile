FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY entrypoint.sh /usr/local/bin/checker-entrypoint.sh
COPY . /app
RUN chmod +x /usr/local/bin/checker-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/checker-entrypoint.sh"]
CMD ["python", "main.py"]
