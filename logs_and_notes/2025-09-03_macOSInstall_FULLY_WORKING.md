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


brew install labstreaminglayer/tap/lsl cmake qt micromamba


### First time setup
```bash
git clone https://github.com/CommanderPho/emotiv-lsl.git
cd emotiv-lsl/
git clone https://github.com/CommanderPho/hidapi.git
cd hidapi
cd mac
make -f Makefile-manual

micromamba create -n lsl_env python=3.8
micromamba activate lsl_env
micromamba install -c conda-forge liblsl
micromamba install attrs nptyping typing_extensions
pip install -r requirements_for_mamba.txt

```

### Also did `manual UV add for hid`, but not sure if this is important
```bash
uv add "hid==1.0.4"
```



### Almost working phasE:
```
(lsl_env) pho@rMBP-PinkDot emotiv-lsl % python main.py 
Traceback (most recent call last):
  File "main.py", line 2, in <module>
    from emotiv_lsl.emotiv_epoc_x import EmotivEpocX
  File "/Users/pho/repos/PhoEmotivWorkspace/emotiv-lsl/emotiv_lsl/emotiv_epoc_x.py", line 1, in <module>
    import hid
  File "/Users/pho/mambaforge/envs/lsl_env/lib/python3.8/site-packages/hid/__init__.py", line 30, in <module>
    raise ImportError(error)
ImportError: Unable to load any of the following libraries:libhidapi-hidraw.so libhidapi-hidraw.so.0 libhidapi-libusb.so libhidapi-libusb.so.0 libhidapi-iohidmanager.so libhidapi-iohidmanager.so.0 libhidapi.dylib hidapi.dll libhidapi-0.dll
(lsl_env) pho@rMBP-PinkDot emotiv-lsl % 
```


### Fix by cloning `hidapi`
```bash
git clone https://github.com/CommanderPho/hidapi.git
cd hidapi
cd mac
make -f Makefile-manual

```
