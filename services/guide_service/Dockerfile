FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg grep && rm -rf /var/lib/apt/lists/*
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app /code/app
COPY .env /code/.env
COPY data /code/data
EXPOSE 80
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]