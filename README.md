# Emotiv-LSL Documentation
"""
# Emotiv-LSL
## Description
Serveur LSL (Lab Streaming Layer) pour le casque Emotiv EPOC X, basé sur le projet original [CyKit] et [emotiv] (https://github.com/vtr0n/emotiv-lsl). Ce projet permet d'acquérir, lire et exporter les données brutes du casque.

---

## Prérequis
### Dépendances
- **Python 3.8** : Créez un environnement conda dédié.
- **Liblsl** : Installez la bibliothèque LSL pour Python.
- **Packages supplémentaires** : Utilisez `requirements.txt` pour installer les dépendances nécessaires.

---

## Installation
### Étapes de base
1. **Créer un environnement conda** : 
   ```bash
   conda create -n lsl_env python=3.8
   ```
2. **Activer l'environnement** :
   ```bash
   conda activate lsl_env
   ```
3. **Installer les dépendances** :
   ```bash
   conda install -c conda-forge liblsl
   pip install -r requirements.txt
   ```

---

## Utilisation
1. **Connecter le dongle et allumer le casque** :
   - Assurez-vous que les indicateurs lumineux signalent une connexion active.
2. **Lancer le serveur LSL** :
   ```bash
   python main.py
   ```
3. **Visualiser le signal** :
   - Dans l'environnement conda, installez et lancez `bsl_stream_viewer` :
     ```bash
     pip install bsl
     bsl_stream_viewer
     ```

---

## Docker
### Installation et exécution
1. **Configurer le projet Docker** :
   ```bash
   chmod +x ./setup_emotiv_docker.sh
   sudo ./setup_emotiv_docker.sh
   ```
2. **Lancer les conteneurs Docker** :
   ```bash
   sudo docker-compose up
   ```
3. **Alternative avec `docker run`** :
   ```bash
   docker run -d \
     --name emotiv \
     --privileged \
     --device /dev/bus/usb:/dev/bus/usb \
     -v $(pwd):/app \
     -e PYTHONUNBUFFERED=1 \
     thefleur075/python_pylsl_emotiv \
     conda run -n lsl_env python main.py
   ```

---

## Exemples d'utilisation
### Acquisition de données brutes
1. Lancer le serveur LSL :
   ```bash
   python main.py &
   ```
2. Lire les données brutes :
   ```bash
   python examples/read_data.py
   ```

### Exportation des données avec MNE
1. Lancer le serveur LSL :
   ```bash
   python main.py &
   ```
2. Exporter les données dans un fichier `.fif` :
   ```bash
   python examples/read_and_export_mne.py
   ```

---

## Roadmap
- **Support Windows** : Actuellement en développement.

---

## Ressources
- Projet original : [Emotiv-LSL sur GitHub](https://github.com/vtr0n/emotiv-lsl)

--- 