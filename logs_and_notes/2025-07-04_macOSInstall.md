```bash
brew install hidapi libusb usbutils wireshark tcpdump
brew install labstreaminglayer/tap/lsl
pyenv local 3.11.9
uv python pin 3.11.9
uv sync
source .venv/bin/activate
```


10037  
10038* python main.py
10039* DYLD_LIBRARY_PATH=/usr/local/lib python main.py

2025-07-04_1049am - Error after correct install
```bash
Traceback (most recent call last):
  File "/Users/pho/repo/EmotivEpocRepos2025/emotiv-lsl/main.py", line 7, in <module>
    emotiv_epoc_x.main_loop()
  File "/Users/pho/repo/EmotivEpocRepos2025/emotiv-lsl/emotiv_lsl/emotiv_base.py", line 23, in main_loop
    hid_device = hid.Device(path=device['path'])
                 ^^^^^^^^^^
AttributeError: module 'hid' has no attribute 'Device'. Did you mean: 'device'?
(emotiv-lsl) ➜  emotiv-lsl git:(develop) ✗ 
```



## 2025-08-08 - rMBP via micromamba
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