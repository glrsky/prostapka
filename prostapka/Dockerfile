# Stage 1: Użyj oficjalnego obrazu Pythona jako bazowego obrazu
FROM python:3.10-slim-buster

# Utwórz i ustaw katalog roboczy
WORKDIR /prostapka

# Skopiuj plik requirements.txt do kontenera
COPY requirements.txt /prostapka/

# Zainstaluj zależności
RUN pip install -r requirements.txt

# Skopiuj resztę plików do kontenera
COPY . /prostapka/

# Utwórz i ustaw katalog roboczy
WORKDIR /prostapka

# Skopiuj pliki i zależności z poprzedniego etapu (builder)
COPY . /prostapka/

VOLUME ["prostabka_db"]

# Ustaw zmienne środowiskowe
ENV PYTHONUNBUFFERED=1

# Uruchom migracje i startuj serwer
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
