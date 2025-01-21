# Utiliser une image de base appropriée
FROM python:3.10-slim

# Installer les dépendances système nécessaires pour compiler mysqlclient
RUN apt-get update && apt-get install -y \
    gcc \
    libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Créer un répertoire pour l'application et se positionner dedans
WORKDIR /app

# Copier le fichier requirements.txt
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code de l'application
COPY . .

# Exposer le port si nécessaire
EXPOSE 5000

# Lancer l'application Flask
CMD ["python", "main.py"]

