#!/bin/bash

# Mot-clé pour identifier le dongle Emotiv dans la description lsusb
EMOTIV_KEYWORD="Emotiv"

echo "Recherche du dongle Emotiv dans lsusb..."

# Trouver la ligne contenant le dongle Emotiv
DEVICE_INFO=$(lsusb | grep "$EMOTIV_KEYWORD")

if [ -z "$DEVICE_INFO" ]; then
    echo "Erreur : Dongle Emotiv introuvable. Vérifiez qu'il est bien connecté."
    exit 1
fi

echo "Périphérique Emotiv détecté : $DEVICE_INFO"

# Extraire Bus, Device et ID
BUS=$(echo "$DEVICE_INFO" | awk '{print $2}')
DEVICE=$(echo "$DEVICE_INFO" | awk '{print $4}' | sed 's/://')
USB_ID=$(echo "$DEVICE_INFO" | awk '{print $6}')

# Construire le chemin complet
DEVICE_PATH="/dev/bus/usb/$BUS/$DEVICE"

# Vérifier si le périphérique existe
if [ ! -e "$DEVICE_PATH" ]; then
    echo "Erreur : Le chemin du périphérique ($DEVICE_PATH) n'existe pas."
    exit 1
fi

echo "Chemin USB détecté : $DEVICE_PATH"
echo "ID USB détecté : $USB_ID"

# Générer ou mettre à jour docker-compose.yml
DOCKER_COMPOSE_FILE="docker-compose.yml"

cat > $DOCKER_COMPOSE_FILE <<EOF
version: '3.8'

services:
  python-app:
    devices:
      - /dev/hidraw0:/dev/hidraw0
      - /dev/hidraw1:/dev/hidraw1
      - ${DEVICE_PATH}:${DEVICE_PATH}
    build: .
    container_name: python_pylsl_emotiv
    privileged: true
    volumes:
      - .:/app
    environment:
      - PYTHONUNBUFFERED=1
      - USB_DEVICE=$USB_ID
    command: ["conda", "run", "-n", "lsl_env", "python", "main.py"]
EOF

echo "Fichier $DOCKER_COMPOSE_FILE mis à jour avec succès !"
echo "Le dongle Emotiv est configuré pour Docker."

# Lancer Docker Compose avec le périphérique détecté
echo "Lancement de Docker Compose..."
docker-compose up --build
