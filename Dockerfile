FROM python:3.10-slim

# Installa ffmpeg e dipendenze di base
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    pip install --no-cache-dir flask basic-pitch torch librosa ffmpeg-python

# Copia i file dell'app
COPY . /app
WORKDIR /app

# Avvia l'app Flask
CMD ["python", "app.py"]
