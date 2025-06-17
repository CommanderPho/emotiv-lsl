# Emotiv-LSL Documentation

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
   sudo docker-compose build
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
   python main.py
   ```
2. Lire les données brutes :
   ```bash
   python examples/read_data.py
   ```

### Exportation des données avec MNE
1. Lancer le serveur LSL :
   ```bash
   python main.py
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



## 2025-05-30 - Pho WindowsVM Setup

python main.py
```ps1
(.venv) PS C:\Users\pho\repos\emotiv-lsl> history

  Id CommandLine
  -- -----------
   1 cd .\repos\
   2 ls
   3 pwd
   4 git clone https://github.com/CommanderPho/emotiv-lsl.git
   5 cd .\emotiv-lsl\
   6 ls
   7 code .
   8 pyenv local
   9 pyenv
  10 pyenv exec python -m pip install pipenv
  11 pyenv exec python -m pip install --upgrade pip
  12 pyenv exec python -m pip install venv
  13 pyenv exec python -m venv .venv
  14 .\.venv\Scripts\Activate.ps1
  15 pyenv local .\.venv\Scripts\python.exe
  16 python -m pip install --upgrade pip
  17 python -m pip install pipenv
  18 python -m pipenv install
  19 python -m pip install bsl
  ```


## 2025-06-17 - Actually working on DietPiVMWareEEG.local (via SSH)
```
git clone https://github.com/CommanderPho/emotiv-lsl.git
cd emotiv-lsl/
ls
mamba
deactivate
conda deactivate
ls
mamba create -n lsl_env python=3.8
mamba activate lsl_env
mamba install -c conda-forge liblsl
pip install -r requirements.txt
python main.py
sudo apt update
sudo apt install -y libhidapi-dev libhidapi-hidraw0 libhidapi-libusb0 libusb-1.0-0-dev build-essential
sudo apt update
ls
python main.py

```