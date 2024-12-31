# Utiliser l'image Miniconda comme base
FROM continuumio/miniconda

# Créer et activer l'environnement conda
RUN conda create -y --name lsl_env python=3.8
SHELL ["conda", "run", "-n", "lsl_env", "/bin/bash", "-c"]

# Mettre à jour les sources Debian et installer les dépendances nécessaires
RUN sed -i 's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' /etc/apt/sources.list && \
    sed -i '/security.debian.org/d' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y libhidapi-dev libhidapi-hidraw0 libhidapi-libusb0 libusb-1.0-0-dev build-essential

# Installer liblsl (Bibliothèque pour l'acquisition de signaux via LSL)
RUN conda install -y -c conda-forge liblsl

# Configurer les liens symboliques pour les bibliothèques partagées
RUN ldconfig

# Copier les fichiers du projet dans l'image
COPY . /app

# Définir le répertoire de travail
WORKDIR /app

# Mettre à jour pip et installer les dépendances Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt --no-cache-dir

# Ajouter PYTHONPATH pour inclure les fichiers locaux
ENV PYTHONPATH="/app:$PYTHONPATH"

# Point d'entrée par défaut
CMD ["conda", "run", "-n", "lsl_env", "python", "main.py"]
