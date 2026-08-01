FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

RUN useradd --create-home --uid 10001 appuser
USER 10001

ENV PYTHONPATH=/app
EXPOSE 8080

CMD ["python", "src/app.py"]
