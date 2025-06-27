# Emotiv-LSL Documentation

# Emotiv-LSL
## Description
LSL (Lab Streaming Layer) server for the Emotiv EPOC X headset, based on the original [CyKit] and [emotiv] (https://github.com/vtr0n/emotiv-lsl) project. This project allows acquiring, reading, and exporting raw data from the headset.

---

## Prerequisites
### Dependencies
- **Python 3.8**: Create a dedicated conda environment.
- **Liblsl**: Install the LSL library for Python.
- **Additional packages**: Use `requirements.txt` to install necessary dependencies.

---

## Installation
### Basic Steps
1. **Create a conda environment**: 
   ```bash
   conda create -n lsl_env python=3.8
   ```
2. **Activate the environment**:
   ```bash
   conda activate lsl_env
   ```
3. **Install dependencies**:
   ```bash
   conda install -c conda-forge liblsl
   pip install -r requirements.txt
   ```

---

## Usage
1. **Connect the dongle and turn on the headset**:
   - Make sure the indicator lights signal an active connection.
2. **Launch the LSL server**:
   ```bash
   python main.py
   ```
3. **Visualize the signal**:
   - In the conda environment, install and launch `bsl_stream_viewer`:
     ```bash
     pip install bsl
     bsl_stream_viewer
     ```

---

## Docker
### Installation and Execution
1. **Configure the Docker project**:
   ```bash
   chmod +x ./setup_emotiv_docker.sh
   sudo ./setup_emotiv_docker.sh
   ```
2. **Launch Docker containers**:
   ```bash
   sudo docker-compose build
   sudo docker-compose up
   ```
3. **Alternative with `docker run`**:
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

## Usage Examples
### Raw Data Acquisition
1. Launch the LSL server:
   ```bash
   python main.py
   ```
2. Read raw data:
   ```bash
   python examples/read_data.py
   ```

### Data Export with MNE
1. Launch the LSL server:
   ```bash
   python main.py
   ```
2. Export data to a `.fif` file:
   ```bash
   python examples/read_and_export_mne.py
   ```

---

## Roadmap
- **Windows Support**: Currently in development.

---

## Resources
- Original project: [Emotiv-LSL on GitHub](https://github.com/vtr0n/emotiv-lsl)

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


## 2025-06-17 - Actually working on EpocXTestingClone (Win10 VM)
```
git clone https://github.com/CommanderPho/emotiv-lsl.git
cd emotiv-lsl/
micromamba create -n lsl_env python=3.8
micromamba activate lsl_env
micromamba install -c conda-forge liblsl
pip install -r requirements_for_mamba.txt
python main.py
ls
python main.py

```

Mamba python env path: `"C:\Users\pho\micromamba\envs\lsl_env\python.exe"`


### Had to install `hidapi-win` manually:
1. Downloaded the latest release from https://github.com/libusb/hidapi/releases
[hidapi-releases](https://github.com/libusb/hidapi/releases/tag/hidapi-0.15.0) and unzippped it in the `emotiv-lsl` folder.
```
hidapi-win
 ┣ include
 ┃ ┣ hidapi.h
 ┃ ┗ hidapi_winapi.h
 ┣ x64
 ┃ ┣ hidapi.dll
 ┃ ┣ hidapi.lib
 ┃ ┗ hidapi.pdb
 ┗ x86
 ┃ ┣ hidapi.dll
 ┃ ┣ hidapi.lib
 ┃ ┗ hidapi.pdb
 ```

```
copy "C:\Users\pho\repos\emotiv-lsl\hidapi-win\x64\hidapi.dll" "C:\Users\pho\micromamba\envs\lsl_env\Library\bin\"
```


## SUCESS - 2023-06-18 - Got Completely working with my new Emotiv Epoc X via USB reciever.
I discovered that you have to launch several terminals: 
1. first the server: `python main.py`, 
2. then the logger/file writer `examples/pho_read_and_export_mne.py`
3. Optionally, you can also visualize the results with: `bsl_stream_viewer`.



copy "C:\Users\pho\repos\emotiv-lsl\hidapi-win\x64\hidapi.dll" "C:\Users\pho\micromamba\envs\lsl_env\Library\bin\"

copy hidapi-win\x64\hidapi.dll "K:\FastSwap\Environments\micromamba\envs\lsl_env\Library\bin\"

copy hidapi-win\x64\hidapi.dll "C:\Users\pho\micromamba\envs\lsl_env\Library\bin\"

```

# Running

In two separate terminal tabs:
1. Activate the conda environment, launch the server backend
```ps1
micromamba activate lsl_env
python main.py
```

2. Launch the `bsl_stream_viewer`:
   ```ps1
micromamba activate lsl_env
bsl_stream_viewer
   ```

