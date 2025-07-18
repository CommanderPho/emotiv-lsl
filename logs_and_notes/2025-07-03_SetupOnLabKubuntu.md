## Fixing Linux hid.HIDException errors
```bash
Traceback (most recent call last):
  File "main.py", line 7, in <module>
    emotiv_epoc_x.main_loop()
  File "/home/halechr/repos/emotiv-lsl/emotiv_lsl/emotiv_base.py", line 23, in main_loop
    hid_device = hid.Device(path=device['path'])
  File "/home/halechr/miniforge3/envs/lsl_env/lib/python3.8/site-packages/hid/__init__.py", line 130, in __init__
    raise HIDException('unable to open device')
hid.HIDException: unable to open device
```


```bash
(lsl_env) halechr@RDLU0039:~/repos/emotiv-lsl$ ls /dev/hid*
/dev/hidraw0  /dev/hidraw1  /dev/hidraw2  /dev/hidraw3  /dev/hidraw4  /dev/hidraw5  /dev/hidraw6
(lsl_env) halechr@RDLU0039:~/repos/emotiv-lsl$ ls /dev/
Display all 332 possibilities? (y or n)
autofs            dm-4              hidraw4           log               loop23            loop39            loop54            loop7             loop-control      nvidia-uvm        rtc0              tty               tty23             tty39             tty54             ttyS10            ttyS26            usb/              vcsa3             vmci
block/            dm-5              hidraw5           loop0             loop24            loop4             loop55            loop70            mapper/           nvidia-uvm-tools  sda               tty0              tty24             tty4              tty55             ttyS11            ttyS27            userfaultfd       vcsa4             vmmon
bsg/              dm-6              hidraw6           loop1             loop25            loop40            loop56            loop71            mcelog            nvme0             sda1              tty1              tty25             tty40             tty56             ttyS12            ttyS28            userio            vcsa5             vmnet0
btrfs-control     dm-7              hpet              loop10            loop26            loop41            loop57            loop72            mei0              nvme0n1           sdb               tty10             tty26             tty41             tty57             ttyS13            ttyS29            vboxdrv           vcsa6             vmnet1
bus/              dm-8              hugepages/        loop11            loop27            loop42            loop58            loop73            mem               nvme0n1p1         sdb1              tty11             tty27             tty42             tty58             ttyS14            ttyS3             vboxdrvu          vcsu              vmnet8
cdrom             dma_heap/         hwrng             loop12            loop28            loop43            loop59            loop74            mqueue/           nvme0n1p2         sg0               tty12             tty28             tty43             tty59             ttyS15            ttyS30            vboxnetctl        vcsu1             vsock
char/             dri/              i2c-0             loop13            loop29            loop44            loop6             loop75            mtd0              nvme0n1p3         sg1               tty13             tty29             tty44             tty6              ttyS16            ttyS31            vboxusb/          vcsu2             wmi/
console           ecryptfs          i2c-1             loop14            loop3             loop45            loop60            loop76            mtd0ro            nvram             sg2               tty14             tty3              tty45             tty60             ttyS17            ttyS4             vcs               vcsu3             zero
core              fb0               i2c-2             loop15            loop30            loop46            loop61            loop77            mtd1              port              shm/              tty15             tty30             tty46             tty61             ttyS18            ttyS5             vcs1              vcsu4             zfs
cpu/              fd/               i2c-3             loop16            loop31            loop47            loop62            loop78            mtd1ro            ppp               snapshot          tty16             tty31             tty47             tty62             ttyS19            ttyS6             vcs2              vcsu5             
cpu_dma_latency   full              i2c-4             loop17            loop32            loop48            loop63            loop79            net/              psaux             snd/              tty17             tty32             tty48             tty63             ttyS2             ttyS7             vcs3              vcsu6             
cuse              fuse              i2c-5             loop18            loop33            loop49            loop64            loop8             ng0n1             ptmx              sr0               tty18             tty33             tty49             tty7              ttyS20            ttyS8             vcs4              vfio/             
disk/             gpiochip0         initctl           loop19            loop34            loop5             loop65            loop80            null              ptp0              stderr            tty19             tty34             tty5              tty8              ttyS21            ttyS9             vcs5              vg0/              
dm-0              hidraw0           input/            loop2             loop35            loop50            loop66            loop81            nvidia0           pts/              stdin             tty2              tty35             tty50             tty9              ttyS22            udmabuf           vcs6              vga_arbiter       
dm-1              hidraw1           isst_interface    loop20            loop36            loop51            loop67            loop82            nvidia-caps/      random            stdout            tty20             tty36             tty51             ttyprintk         ttyS23            uhid              vcsa              vhci              
dm-2              hidraw2           kmsg              loop21            loop37            loop52            loop68            loop83            nvidiactl         rfkill            tpm0              tty21             tty37             tty52             ttyS0             ttyS24            uinput            vcsa1             vhost-net         
dm-3              hidraw3           kvm               loop22            loop38            loop53            loop69            loop9             nvidia-modeset    rtc               tpmrm0            tty22             tty38             tty53             ttyS1             ttyS25            urandom           vcsa2             vhost-vsock       
(lsl_env) halechr@RDLU0039:~/repos/emotiv-lsl$ lsusb
Bus 002 Device 003: ID 05e3:0612 Genesys Logic, Inc. Hub
Bus 002 Device 002: ID 0bda:0411 Realtek Semiconductor Corp. Hub
Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
Bus 001 Device 005: ID 046d:c537 Logitech, Inc. Cordless Mouse Receiver
Bus 001 Device 004: ID 046d:c335 Logitech, Inc. G910 Orion Spectrum Mechanical Keyboard
Bus 001 Device 003: ID 05e3:0610 Genesys Logic, Inc. Hub
Bus 001 Device 009: ID 1234:ed02 Brain Actuated Technologies Emotiv EPOC Developer Headset Wireless Dongle
Bus 001 Device 002: ID 0bda:5411 Realtek Semiconductor Corp. RTS5411 Hub
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
```

# Finally worked 2025-07-03:
https://askubuntu.com/questions/15570/configure-udev-to-change-permissions-on-usb-hid-device

```bash
(lsl_env) halechr@RDLU0039:~/repos/emotiv-lsl$ sudo chmod 0666 /dev/hidraw
chmod: cannot access '/dev/hidraw': No such file or directory
(lsl_env) halechr@RDLU0039:~/repos/emotiv-lsl$ sudo chmod 0666 /dev/hidraw*
(lsl_env) halechr@RDLU0039:~/repos/emotiv-lsl$ python main.py 
```


## Lab Computer: Recording to '/home/halechr/FastData/Personal/LabRecordedEEG'

----

## Full log of setup on Lab Workstation (2025-07-03):
```bash
halechr@RDLU0039:~/repos/emotiv-lsl$ sudo apt-get install -y libhidapi-dev libhidapi-hidraw0 libhidapi-libusb0 libusb-1.0-0-dev build-essential usbutils wireshark-common tshark tcpdump udev
halechr@RDLU0039:~/repos/emotiv-lsl$ source .venv/bin/activate
(emotiv-lsl) halechr@RDLU0039:~/repos/emotiv-lsl$ python main.py 
Traceback (most recent call last):
  File "main.py", line 1, in <module>
    from emotiv_lsl.emotiv_epoc_x import EmotivEpocX
  File "/home/halechr/repos/emotiv-lsl/emotiv_lsl/emotiv_epoc_x.py", line 1, in <module>
    import hid
ModuleNotFoundError: No module named 'hid'


```

### Found `mamba` was installed and siwtched to that.
```bash
(emotiv-lsl) halechr@RDLU0039:~/repos/emotiv-lsl$ mamba create -n lsl_env python=3.8

Looking for: ['python=3.8']

warning  libmamba Could not parse mod/etag header
warning  libmamba Could not parse mod/etag header
conda-forge/noarch                                  21.1MB @  41.3MB/s  0.5s
conda-forge/linux-64                                44.8MB @  59.6MB/s  0.8s
Transaction

  Prefix: /home/halechr/miniforge3/envs/lsl_env

  Updating specs:

   - python=3.8


  Package               Version  Build               Channel           Size
─────────────────────────────────────────────────────────────────────────────
  Install:
─────────────────────────────────────────────────────────────────────────────

  + ca-certificates   2025.6.15  hbd8a1cb_0          conda-forge      151kB
  + _libgcc_mutex           0.1  conda_forge         conda-forge     Cached
  + libgomp              15.1.0  h767d61c_3          conda-forge      447kB
  + ld_impl_linux-64       2.43  h1423503_5          conda-forge      671kB
  + _openmp_mutex           4.5  2_gnu               conda-forge     Cached
  + libgcc               15.1.0  h767d61c_3          conda-forge      825kB
  + openssl               3.5.1  h7b32b05_0          conda-forge        3MB
  + ncurses                 6.5  h2d0b736_3          conda-forge      892kB
  + libzlib               1.3.1  hb9d3cd8_2          conda-forge       61kB
  + libnsl                2.0.1  hb9d3cd8_1          conda-forge       34kB
  + libgcc-ng            15.1.0  h69a702a_3          conda-forge       29kB
  + liblzma               5.8.1  hb9d3cd8_2          conda-forge      113kB
  + libffi                3.4.6  h2dba641_1          conda-forge       57kB
  + readline                8.2  h8c095d6_2          conda-forge      282kB
  + libsqlite            3.50.2  h6cd9bfd_0          conda-forge      919kB
  + tk                   8.6.13  noxft_hd72426e_102  conda-forge        3MB
  + libxcrypt            4.4.36  hd590300_1          conda-forge     Cached
  + bzip2                 1.0.8  h4bc722e_7          conda-forge     Cached
  + libuuid              2.38.1  h0b41bf4_0          conda-forge     Cached
  + xz-tools              5.8.1  hb9d3cd8_2          conda-forge       96kB
  + xz-gpl-tools          5.8.1  hbcc6ac9_2          conda-forge       34kB
  + liblzma-devel         5.8.1  hb9d3cd8_2          conda-forge      440kB
  + xz                    5.8.1  hbcc6ac9_2          conda-forge       24kB
  + python               3.8.20  h4a871b0_2_cpython  conda-forge       22MB
  + wheel                0.45.1  pyhd8ed1ab_0        conda-forge       63kB
  + setuptools           75.3.0  pyhd8ed1ab_0        conda-forge      780kB
  + pip                  24.3.1  pyh8b19718_0        conda-forge        1MB

  Summary:

  Install: 27 packages

  Total download: 36MB

─────────────────────────────────────────────────────────────────────────────


Confirm changes: [Y/n] Y
Confirm changes: [Y/n] Y
ca-certificates                                    151.1kB @   1.6MB/s  0.1s
libgomp                                            447.1kB @   3.9MB/s  0.1s
ld_impl_linux-64                                   670.6kB @   5.4MB/s  0.1s
libffi                                              57.4kB @ 418.8kB/s  0.0s
liblzma-devel                                      439.9kB @   2.5MB/s  0.1s
libgcc                                             824.9kB @   4.4MB/s  0.2s
wheel                                               63.0kB @ 314.5kB/s  0.1s
openssl                                              3.1MB @  15.2MB/s  0.2s
tk                                                   3.3MB @  15.3MB/s  0.1s
ncurses                                            891.6kB @   4.0MB/s  0.0s
libgcc-ng                                           29.0kB @ 129.8kB/s  0.0s
liblzma                                            112.9kB @ 441.2kB/s  0.0s
libsqlite                                          918.9kB @   3.5MB/s  0.1s
xz-gpl-tools                                        33.9kB @ 125.6kB/s  0.0s
pip                                                  1.2MB @   4.5MB/s  0.1s
xz                                                  24.0kB @  84.4kB/s  0.1s
libzlib                                             61.0kB @ 209.8kB/s  0.0s
libnsl                                              33.7kB @ 107.8kB/s  0.0s
xz-tools                                            96.4kB @ 301.5kB/s  0.1s
readline                                           282.5kB @ 850.5kB/s  0.0s
setuptools                                         779.6kB @   2.2MB/s  0.1s
python                                              22.2MB @  40.3MB/s  0.3s

Downloading and Extracting Packages:

Preparing transaction: done
Verifying transaction: done
Executing transaction: done

To activate this environment, use

     $ mamba activate lsl_env

To deactivate an active environment, use

     $ mamba deactivate

(emotiv-lsl) halechr@RDLU0039:~/repos/emotiv-lsl$ ^C
(emotiv-lsl) halechr@RDLU0039:~/repos/emotiv-lsl$ mamba create -n lsl_env python=3.8
WARNING: A conda environment already exists at '/home/halechr/miniforge3/envs/lsl_env'
Remove existing environment (y/[n])? n
mamba install -c conda-forge liblslnnv
WARNING: A conda environment already exists at '/home/halechr/miniforge3/envs/lsl_env'
Remove existing environment (y/[n])? ^C
Operation aborted.  Exiting.

CondaSystemExit: 
Operation aborted.  Exiting.

(emotiv-lsl) halechr@RDLU0039:~/repos/emotiv-lsl$ mamba activate lsl_env
(lsl_env) (emotiv-lsl) halechr@RDLU0039:~/repos/emotiv-lsl$ mamba install -c conda-forge liblsl

Looking for: ['liblsl']

conda-forge/linux-64                                        Using cache
conda-forge/noarch                                          Using cache

Pinned packages:
  - python 3.8.*


Transaction

  Prefix: /home/halechr/miniforge3/envs/lsl_env

  Updating specs:

   - liblsl
   - ca-certificates
   - openssl


  Package      Version  Build       Channel          Size
───────────────────────────────────────────────────────────
  Install:
───────────────────────────────────────────────────────────

  + libstdcxx   15.1.0  h8f9b012_3  conda-forge       4MB
  + pugixml       1.15  h3f63f65_0  conda-forge     118kB
  + liblsl      1.16.2  h4e8d35e_3  conda-forge     387kB

  Summary:

  Install: 3 packages

  Total download: 4MB

───────────────────────────────────────────────────────────


Confirm changes: [Y/n] Y
liblsl                                             387.1kB @   2.3MB/s  0.2s
libstdcxx                                            3.9MB @  18.6MB/s  0.2s
pugixml                                            118.5kB @ 456.5kB/s  0.3s

Downloading and Extracting Packages:

Preparing transaction: done
Verifying transaction: done
Executing transaction: done
(lsl_env) (emotiv-lsl) halechr@RDLU0039:~/repos/emotiv-lsl$ deactivate 
halechr@RDLU0039:~/repos/emotiv-lsl$ mamba deactivate
halechr@RDLU0039:~/repos/emotiv-lsl$ deactivate
deactivate: command not found
halechr@RDLU0039:~/repos/emotiv-lsl$ mamba activate lsl_env
(lsl_env) halechr@RDLU0039:~/repos/emotiv-lsl$ pip install -r requirements_for_mamba.txt
Collecting certifi==2024.12.14 (from -r requirements_for_mamba.txt (line 1))
  Downloading certifi-2024.12.14-py3-none-any.whl.metadata (2.3 kB)
Collecting charset-normalizer==3.4.1 (from -r requirements_for_mamba.txt (line 2))
  Downloading charset_normalizer-3.4.1-cp38-cp38-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (35 kB)
Collecting contourpy==1.1.1 (from -r requirements_for_mamba.txt (line 3))
  Downloading contourpy-1.1.1-cp38-cp38-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (5.9 kB)
Collecting cycler==0.12.1 (from -r requirements_for_mamba.txt (line 4))
  Using cached cycler-0.12.1-py3-none-any.whl.metadata (3.8 kB)
Collecting decorator==5.1.1 (from -r requirements_for_mamba.txt (line 5))
  Using cached decorator-5.1.1-py3-none-any.whl.metadata (4.0 kB)
Collecting fonttools==4.55.3 (from -r requirements_for_mamba.txt (line 6))
  Downloading fonttools-4.55.3-cp38-cp38-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (165 kB)
Collecting hid==1.0.4 (from -r requirements_for_mamba.txt (line 7))
  Downloading hid-1.0.4.tar.gz (3.9 kB)
  Preparing metadata (setup.py) ... done
Collecting idna==3.10 (from -r requirements_for_mamba.txt (line 8))
  Downloading idna-3.10-py3-none-any.whl.metadata (10 kB)
Collecting importlib_resources==6.4.5 (from -r requirements_for_mamba.txt (line 9))
  Downloading importlib_resources-6.4.5-py3-none-any.whl.metadata (4.0 kB)
Collecting Jinja2==3.1.5 (from -r requirements_for_mamba.txt (line 10))
  Downloading jinja2-3.1.5-py3-none-any.whl.metadata (2.6 kB)
Collecting kiwisolver==1.4.7 (from -r requirements_for_mamba.txt (line 11))
  Downloading kiwisolver-1.4.7-cp38-cp38-manylinux_2_5_x86_64.manylinux1_x86_64.whl.metadata (6.3 kB)
Collecting lazy_loader==0.4 (from -r requirements_for_mamba.txt (line 12))
  Using cached lazy_loader-0.4-py3-none-any.whl.metadata (7.6 kB)
Collecting MarkupSafe==2.1.5 (from -r requirements_for_mamba.txt (line 13))
  Downloading MarkupSafe-2.1.5-cp38-cp38-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (3.0 kB)
Collecting matplotlib==3.7.5 (from -r requirements_for_mamba.txt (line 14))
  Downloading matplotlib-3.7.5-cp38-cp38-manylinux_2_12_x86_64.manylinux2010_x86_64.whl.metadata (5.7 kB)
Collecting mne==1.6.1 (from -r requirements_for_mamba.txt (line 15))
  Downloading mne-1.6.1-py3-none-any.whl.metadata (13 kB)
Collecting numpy==1.24.4 (from -r requirements_for_mamba.txt (line 16))
  Downloading numpy-1.24.4-cp38-cp38-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (5.6 kB)
Collecting packaging==24.2 (from -r requirements_for_mamba.txt (line 17))
  Using cached packaging-24.2-py3-none-any.whl.metadata (3.2 kB)
Collecting pillow==10.4.0 (from -r requirements_for_mamba.txt (line 18))
  Downloading pillow-10.4.0-cp38-cp38-manylinux_2_28_x86_64.whl.metadata (9.2 kB)
Collecting platformdirs==4.3.6 (from -r requirements_for_mamba.txt (line 19))
  Using cached platformdirs-4.3.6-py3-none-any.whl.metadata (11 kB)
Collecting pooch==1.8.2 (from -r requirements_for_mamba.txt (line 20))
  Using cached pooch-1.8.2-py3-none-any.whl.metadata (10 kB)
Collecting pycryptodome==3.21.0 (from -r requirements_for_mamba.txt (line 21))
  Downloading pycryptodome-3.21.0-cp36-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (3.4 kB)
Collecting pylsl==1.16.2 (from -r requirements_for_mamba.txt (line 22))
  Downloading pylsl-1.16.2-py2.py3-none-any.whl.metadata (5.7 kB)
Collecting pyparsing==3.1.4 (from -r requirements_for_mamba.txt (line 23))
  Downloading pyparsing-3.1.4-py3-none-any.whl.metadata (5.1 kB)
Collecting python-dateutil==2.9.0.post0 (from -r requirements_for_mamba.txt (line 24))
  Using cached python_dateutil-2.9.0.post0-py2.py3-none-any.whl.metadata (8.4 kB)
Collecting requests==2.32.3 (from -r requirements_for_mamba.txt (line 25))
  Using cached requests-2.32.3-py3-none-any.whl.metadata (4.6 kB)
Collecting scipy==1.10.1 (from -r requirements_for_mamba.txt (line 26))
  Downloading scipy-1.10.1-cp38-cp38-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (58 kB)
Collecting six==1.17.0 (from -r requirements_for_mamba.txt (line 27))
  Using cached six-1.17.0-py2.py3-none-any.whl.metadata (1.7 kB)
Collecting tqdm==4.67.1 (from -r requirements_for_mamba.txt (line 28))
  Downloading tqdm-4.67.1-py3-none-any.whl.metadata (57 kB)
Collecting urllib3==2.2.3 (from -r requirements_for_mamba.txt (line 29))
  Downloading urllib3-2.2.3-py3-none-any.whl.metadata (6.5 kB)
Collecting zipp==3.20.2 (from -r requirements_for_mamba.txt (line 30))
  Using cached zipp-3.20.2-py3-none-any.whl.metadata (3.7 kB)
Downloading certifi-2024.12.14-py3-none-any.whl (164 kB)
Downloading charset_normalizer-3.4.1-cp38-cp38-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (144 kB)
Downloading contourpy-1.1.1-cp38-cp38-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (301 kB)
Using cached cycler-0.12.1-py3-none-any.whl (8.3 kB)
Using cached decorator-5.1.1-py3-none-any.whl (9.1 kB)
Downloading fonttools-4.55.3-cp38-cp38-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (4.7 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.7/4.7 MB 4.0 MB/s eta 0:00:00
Downloading idna-3.10-py3-none-any.whl (70 kB)
Downloading importlib_resources-6.4.5-py3-none-any.whl (36 kB)
Downloading jinja2-3.1.5-py3-none-any.whl (134 kB)
Downloading kiwisolver-1.4.7-cp38-cp38-manylinux_2_5_x86_64.manylinux1_x86_64.whl (1.2 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.2/1.2 MB 3.1 MB/s eta 0:00:00
Using cached lazy_loader-0.4-py3-none-any.whl (12 kB)
Downloading MarkupSafe-2.1.5-cp38-cp38-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (26 kB)
Downloading matplotlib-3.7.5-cp38-cp38-manylinux_2_12_x86_64.manylinux2010_x86_64.whl (9.2 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 9.2/9.2 MB 3.8 MB/s eta 0:00:00
Downloading mne-1.6.1-py3-none-any.whl (8.3 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 8.3/8.3 MB 4.6 MB/s eta 0:00:00
Downloading numpy-1.24.4-cp38-cp38-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (17.3 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 17.3/17.3 MB 4.2 MB/s eta 0:00:00
Using cached packaging-24.2-py3-none-any.whl (65 kB)
Downloading pillow-10.4.0-cp38-cp38-manylinux_2_28_x86_64.whl (4.5 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.5/4.5 MB 6.5 MB/s eta 0:00:00
Using cached platformdirs-4.3.6-py3-none-any.whl (18 kB)
Using cached pooch-1.8.2-py3-none-any.whl (64 kB)
Downloading pycryptodome-3.21.0-cp36-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (2.3 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2.3/2.3 MB 5.0 MB/s eta 0:00:00
Downloading pylsl-1.16.2-py2.py3-none-any.whl (36 kB)
Downloading pyparsing-3.1.4-py3-none-any.whl (104 kB)
Using cached python_dateutil-2.9.0.post0-py2.py3-none-any.whl (229 kB)
Using cached requests-2.32.3-py3-none-any.whl (64 kB)
Downloading scipy-1.10.1-cp38-cp38-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (34.5 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 34.5/34.5 MB 3.9 MB/s eta 0:00:00
Using cached six-1.17.0-py2.py3-none-any.whl (11 kB)
Downloading tqdm-4.67.1-py3-none-any.whl (78 kB)
Downloading urllib3-2.2.3-py3-none-any.whl (126 kB)
Using cached zipp-3.20.2-py3-none-any.whl (9.2 kB)
Building wheels for collected packages: hid
  Building wheel for hid (setup.py) ... done
  Created wheel for hid: filename=hid-1.0.4-py3-none-any.whl size=3781 sha256=263774c8dbb3437ae22bc00342e82f6ca7b01faf6fd6ea15c54785368c1359aa
  Stored in directory: /home/halechr/.cache/pip/wheels/39/95/2a/41fdfff55247dc730d989889d7a99410f9494e538cee45ac3a
Successfully built hid
Installing collected packages: pylsl, hid, zipp, urllib3, tqdm, six, pyparsing, pycryptodome, platformdirs, pillow, packaging, numpy, MarkupSafe, kiwisolver, idna, fonttools, decorator, cycler, charset-normalizer, certifi, scipy, requests, python-dateutil, lazy_loader, Jinja2, importlib_resources, contourpy, pooch, matplotlib, mne
Successfully installed Jinja2-3.1.5 MarkupSafe-2.1.5 certifi-2024.12.14 charset-normalizer-3.4.1 contourpy-1.1.1 cycler-0.12.1 decorator-5.1.1 fonttools-4.55.3 hid-1.0.4 idna-3.10 importlib_resources-6.4.5 kiwisolver-1.4.7 lazy_loader-0.4 matplotlib-3.7.5 mne-1.6.1 numpy-1.24.4 packaging-24.2 pillow-10.4.0 platformdirs-4.3.6 pooch-1.8.2 pycryptodome-3.21.0 pylsl-1.16.2 pyparsing-3.1.4 python-dateutil-2.9.0.post0 requests-2.32.3 scipy-1.10.1 six-1.17.0 tqdm-4.67.1 urllib3-2.2.3 zipp-3.20.2
(lsl_env) halechr@RDLU0039:~/repos/emotiv-lsl$ python main.py 
crypto_key: bytearray(b'6566565666756557')
2025-07-03 10:19:43.222 (   0.006s) [python          ]      netinterfaces.cpp:89    INFO| netif 'lo' (status: 1, multicast: 0, broadcast: 0)
2025-07-03 10:19:43.222 (   0.006s) [python          ]      netinterfaces.cpp:89    INFO| netif 'enp2s0' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 10:19:43.222 (   0.006s) [python          ]      netinterfaces.cpp:89    INFO| netif 'enp0s31f6' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 10:19:43.222 (   0.006s) [python          ]      netinterfaces.cpp:89    INFO| netif 'docker0' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 10:19:43.222 (   0.006s) [python          ]      netinterfaces.cpp:89    INFO| netif 'vmnet1' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 10:19:43.222 (   0.006s) [python          ]      netinterfaces.cpp:89    INFO| netif 'vmnet8' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 10:19:43.222 (   0.006s) [python          ]      netinterfaces.cpp:89    INFO| netif 'veth9cb8d16' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 10:19:43.222 (   0.006s) [python          ]      netinterfaces.cpp:89    INFO| netif 'lo' (status: 1, multicast: 0, broadcast: 0)
2025-07-03 10:19:43.222 (   0.007s) [python          ]      netinterfaces.cpp:89    INFO| netif 'enp0s31f6' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 10:19:43.222 (   0.007s) [python          ]      netinterfaces.cpp:102   INFO|       IPv4 addr: a116954
2025-07-03 10:19:43.222 (   0.007s) [python          ]      netinterfaces.cpp:89    INFO| netif 'docker0' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 10:19:43.222 (   0.007s) [python          ]      netinterfaces.cpp:102   INFO|       IPv4 addr: ac110001
2025-07-03 10:19:43.222 (   0.007s) [python          ]      netinterfaces.cpp:89    INFO| netif 'vmnet1' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 10:19:43.222 (   0.007s) [python          ]      netinterfaces.cpp:102   INFO|       IPv4 addr: ac105801
2025-07-03 10:19:43.222 (   0.007s) [python          ]      netinterfaces.cpp:89    INFO| netif 'vmnet8' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 10:19:43.222 (   0.007s) [python          ]      netinterfaces.cpp:102   INFO|       IPv4 addr: c0a8d801
2025-07-03 10:19:43.222 (   0.007s) [python          ]         api_config.cpp:270   INFO| Loaded default config
2025-07-03 10:19:43.222 (   0.007s) [python          ]             common.cpp:65    INFO| git:/branch:HEAD/build:Release/compiler:GNU-13.3.0/link:SHARED
Traceback (most recent call last):
  File "main.py", line 7, in <module>
    emotiv_epoc_x.main_loop()
  File "/home/halechr/repos/emotiv-lsl/emotiv_lsl/emotiv_base.py", line 23, in main_loop
    hid_device = hid.Device(path=device['path'])
  File "/home/halechr/miniforge3/envs/lsl_env/lib/python3.8/site-packages/hid/__init__.py", line 130, in __init__
    raise HIDException('unable to open device')
hid.HIDException: unable to open device
(lsl_env) halechr@RDLU0039:~/repos/emotiv-lsl$ python main.py 
crypto_key: bytearray(b'6566565666756557')
2025-07-03 10:20:09.732 (   0.004s) [python          ]      netinterfaces.cpp:89    INFO| netif 'lo' (status: 1, multicast: 0, broadcast: 0)
2025-07-03 10:20:09.732 (   0.004s) [python          ]      netinterfaces.cpp:89    INFO| netif 'enp2s0' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 10:20:09.732 (   0.004s) [python          ]      netinterfaces.cpp:89    INFO| netif 'enp0s31f6' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 10:20:09.732 (   0.004s) [python          ]      netinterfaces.cpp:89    INFO| netif 'docker0' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 10:20:09.732 (   0.004s) [python          ]      netinterfaces.cpp:89    INFO| netif 'vmnet1' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 10:20:09.732 (   0.004s) [python          ]      netinterfaces.cpp:89    INFO| netif 'vmnet8' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 10:20:09.732 (   0.004s) [python          ]      netinterfaces.cpp:89    INFO| netif 'veth9cb8d16' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 10:20:09.732 (   0.004s) [python          ]      netinterfaces.cpp:89    INFO| netif 'lo' (status: 1, multicast: 0, broadcast: 0)
2025-07-03 10:20:09.732 (   0.004s) [python          ]      netinterfaces.cpp:89    INFO| netif 'enp0s31f6' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 10:20:09.732 (   0.004s) [python          ]      netinterfaces.cpp:102   INFO|       IPv4 addr: a116954
2025-07-03 10:20:09.732 (   0.004s) [python          ]      netinterfaces.cpp:89    INFO| netif 'docker0' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 10:20:09.732 (   0.004s) [python          ]      netinterfaces.cpp:102   INFO|       IPv4 addr: ac110001
2025-07-03 10:20:09.732 (   0.004s) [python          ]      netinterfaces.cpp:89    INFO| netif 'vmnet1' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 10:20:09.732 (   0.004s) [python          ]      netinterfaces.cpp:102   INFO|       IPv4 addr: ac105801
2025-07-03 10:20:09.732 (   0.004s) [python          ]      netinterfaces.cpp:89    INFO| netif 'vmnet8' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 10:20:09.732 (   0.004s) [python          ]      netinterfaces.cpp:102   INFO|       IPv4 addr: c0a8d801
2025-07-03 10:20:09.732 (   0.004s) [python          ]         api_config.cpp:270   INFO| Loaded default config
2025-07-03 10:20:09.732 (   0.004s) [python          ]             common.cpp:65    INFO| git:/branch:HEAD/build:Release/compiler:GNU-13.3.0/link:SHARED
Traceback (most recent call last):
  File "main.py", line 7, in <module>
    emotiv_epoc_x.main_loop()
  File "/home/halechr/repos/emotiv-lsl/emotiv_lsl/emotiv_base.py", line 23, in main_loop
    hid_device = hid.Device(path=device['path'])
  File "/home/halechr/miniforge3/envs/lsl_env/lib/python3.8/site-packages/hid/__init__.py", line 130, in __init__
    raise HIDException('unable to open device')
hid.HIDException: unable to open device
(lsl_env) halechr@RDLU0039:~/repos/emotiv-lsl$ python main.py 
crypto_key: bytearray(b'6566565666756557')
2025-07-03 12:42:41.316 (   0.005s) [python          ]      netinterfaces.cpp:89    INFO| netif 'lo' (status: 1, multicast: 0, broadcast: 0)
2025-07-03 12:42:41.316 (   0.005s) [python          ]      netinterfaces.cpp:89    INFO| netif 'enp2s0' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 12:42:41.316 (   0.005s) [python          ]      netinterfaces.cpp:89    INFO| netif 'enp0s31f6' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 12:42:41.316 (   0.005s) [python          ]      netinterfaces.cpp:89    INFO| netif 'docker0' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 12:42:41.316 (   0.005s) [python          ]      netinterfaces.cpp:89    INFO| netif 'vmnet1' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 12:42:41.316 (   0.005s) [python          ]      netinterfaces.cpp:89    INFO| netif 'vmnet8' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 12:42:41.316 (   0.005s) [python          ]      netinterfaces.cpp:89    INFO| netif 'lo' (status: 1, multicast: 0, broadcast: 0)
2025-07-03 12:42:41.316 (   0.005s) [python          ]      netinterfaces.cpp:89    INFO| netif 'enp0s31f6' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 12:42:41.316 (   0.005s) [python          ]      netinterfaces.cpp:102   INFO|       IPv4 addr: a116954
2025-07-03 12:42:41.316 (   0.005s) [python          ]      netinterfaces.cpp:89    INFO| netif 'docker0' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 12:42:41.316 (   0.005s) [python          ]      netinterfaces.cpp:102   INFO|       IPv4 addr: ac110001
2025-07-03 12:42:41.316 (   0.005s) [python          ]      netinterfaces.cpp:89    INFO| netif 'vmnet1' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 12:42:41.316 (   0.005s) [python          ]      netinterfaces.cpp:102   INFO|       IPv4 addr: ac105801
2025-07-03 12:42:41.316 (   0.005s) [python          ]      netinterfaces.cpp:89    INFO| netif 'vmnet8' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 12:42:41.316 (   0.005s) [python          ]      netinterfaces.cpp:102   INFO|       IPv4 addr: c0a8d801
2025-07-03 12:42:41.316 (   0.005s) [python          ]         api_config.cpp:270   INFO| Loaded default config
2025-07-03 12:42:41.317 (   0.005s) [python          ]             common.cpp:65    INFO| git:/branch:HEAD/build:Release/compiler:GNU-13.3.0/link:SHARED
Traceback (most recent call last):
  File "main.py", line 7, in <module>
    emotiv_epoc_x.main_loop()
  File "/home/halechr/repos/emotiv-lsl/emotiv_lsl/emotiv_base.py", line 23, in main_loop
    hid_device = hid.Device(path=device['path'])
  File "/home/halechr/miniforge3/envs/lsl_env/lib/python3.8/site-packages/hid/__init__.py", line 130, in __init__
    raise HIDException('unable to open device')
hid.HIDException: unable to open device
(lsl_env) halechr@RDLU0039:~/repos/emotiv-lsl$ sudo python main.py 
[sudo] password for halechr: 
Traceback (most recent call last):
  File "/home/halechr/repos/emotiv-lsl/main.py", line 1, in <module>
    from emotiv_lsl.emotiv_epoc_x import EmotivEpocX
  File "/home/halechr/repos/emotiv-lsl/emotiv_lsl/emotiv_epoc_x.py", line 1, in <module>
    import hid
ModuleNotFoundError: No module named 'hid'
(lsl_env) halechr@RDLU0039:~/repos/emotiv-lsl$ code .
(lsl_env) halechr@RDLU0039:~/repos/emotiv-lsl$ lsusb
Bus 002 Device 003: ID 05e3:0612 Genesys Logic, Inc. Hub
Bus 002 Device 002: ID 0bda:0411 Realtek Semiconductor Corp. Hub
Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
Bus 001 Device 005: ID 046d:c537 Logitech, Inc. Cordless Mouse Receiver
Bus 001 Device 004: ID 046d:c335 Logitech, Inc. G910 Orion Spectrum Mechanical Keyboard
Bus 001 Device 003: ID 05e3:0610 Genesys Logic, Inc. Hub
Bus 001 Device 008: ID 1234:ed02 Brain Actuated Technologies Emotiv EPOC Developer Headset Wireless Dongle
Bus 001 Device 002: ID 0bda:5411 Realtek Semiconductor Corp. RTS5411 Hub
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
(lsl_env) halechr@RDLU0039:~/repos/emotiv-lsl$ sudo cp udev_rules/50-usb-emotivepoc.rules /etc/udev/rules.d/
[sudo] password for halechr: 
(lsl_env) halechr@RDLU0039:~/repos/emotiv-lsl$ sudo udevadm control --reload-rule
(lsl_env) halechr@RDLU0039:~/repos/emotiv-lsl$ sudo udevadm trigger
(lsl_env) halechr@RDLU0039:~/repos/emotiv-lsl$ python main.py 
crypto_key: bytearray(b'6566565666756557')
2025-07-03 13:00:01.390 (   0.004s) [python          ]      netinterfaces.cpp:89    INFO| netif 'lo' (status: 1, multicast: 0, broadcast: 0)
2025-07-03 13:00:01.390 (   0.004s) [python          ]      netinterfaces.cpp:89    INFO| netif 'enp2s0' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 13:00:01.390 (   0.004s) [python          ]      netinterfaces.cpp:89    INFO| netif 'enp0s31f6' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 13:00:01.390 (   0.004s) [python          ]      netinterfaces.cpp:89    INFO| netif 'docker0' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 13:00:01.390 (   0.004s) [python          ]      netinterfaces.cpp:89    INFO| netif 'vmnet1' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 13:00:01.390 (   0.004s) [python          ]      netinterfaces.cpp:89    INFO| netif 'vmnet8' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 13:00:01.390 (   0.004s) [python          ]      netinterfaces.cpp:89    INFO| netif 'lo' (status: 1, multicast: 0, broadcast: 0)
2025-07-03 13:00:01.390 (   0.004s) [python          ]      netinterfaces.cpp:89    INFO| netif 'enp0s31f6' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 13:00:01.390 (   0.004s) [python          ]      netinterfaces.cpp:102   INFO|       IPv4 addr: a116954
2025-07-03 13:00:01.390 (   0.004s) [python          ]      netinterfaces.cpp:89    INFO| netif 'docker0' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 13:00:01.390 (   0.004s) [python          ]      netinterfaces.cpp:102   INFO|       IPv4 addr: ac110001
2025-07-03 13:00:01.390 (   0.004s) [python          ]      netinterfaces.cpp:89    INFO| netif 'vmnet1' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 13:00:01.390 (   0.004s) [python          ]      netinterfaces.cpp:102   INFO|       IPv4 addr: ac105801
2025-07-03 13:00:01.390 (   0.004s) [python          ]      netinterfaces.cpp:89    INFO| netif 'vmnet8' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 13:00:01.390 (   0.004s) [python          ]      netinterfaces.cpp:102   INFO|       IPv4 addr: c0a8d801
2025-07-03 13:00:01.390 (   0.004s) [python          ]         api_config.cpp:270   INFO| Loaded default config
2025-07-03 13:00:01.390 (   0.005s) [python          ]             common.cpp:65    INFO| git:/branch:HEAD/build:Release/compiler:GNU-13.3.0/link:SHARED
Traceback (most recent call last):
  File "main.py", line 7, in <module>
    emotiv_epoc_x.main_loop()
  File "/home/halechr/repos/emotiv-lsl/emotiv_lsl/emotiv_base.py", line 23, in main_loop
    hid_device = hid.Device(path=device['path'])
  File "/home/halechr/miniforge3/envs/lsl_env/lib/python3.8/site-packages/hid/__init__.py", line 130, in __init__
    raise HIDException('unable to open device')
hid.HIDException: unable to open device
(lsl_env) halechr@RDLU0039:~/repos/emotiv-lsl$ python main.py 
crypto_key: bytearray(b'6566565666756557')
2025-07-03 13:00:17.999 (   0.004s) [python          ]      netinterfaces.cpp:89    INFO| netif 'lo' (status: 1, multicast: 0, broadcast: 0)
2025-07-03 13:00:17.999 (   0.004s) [python          ]      netinterfaces.cpp:89    INFO| netif 'enp2s0' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 13:00:17.999 (   0.004s) [python          ]      netinterfaces.cpp:89    INFO| netif 'enp0s31f6' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 13:00:17.999 (   0.004s) [python          ]      netinterfaces.cpp:89    INFO| netif 'docker0' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 13:00:17.999 (   0.004s) [python          ]      netinterfaces.cpp:89    INFO| netif 'vmnet1' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 13:00:17.999 (   0.004s) [python          ]      netinterfaces.cpp:89    INFO| netif 'vmnet8' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 13:00:17.999 (   0.004s) [python          ]      netinterfaces.cpp:89    INFO| netif 'lo' (status: 1, multicast: 0, broadcast: 0)
2025-07-03 13:00:17.999 (   0.004s) [python          ]      netinterfaces.cpp:89    INFO| netif 'enp0s31f6' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 13:00:17.999 (   0.004s) [python          ]      netinterfaces.cpp:102   INFO|       IPv4 addr: a116954
2025-07-03 13:00:17.999 (   0.004s) [python          ]      netinterfaces.cpp:89    INFO| netif 'docker0' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 13:00:17.999 (   0.004s) [python          ]      netinterfaces.cpp:102   INFO|       IPv4 addr: ac110001
2025-07-03 13:00:17.999 (   0.004s) [python          ]      netinterfaces.cpp:89    INFO| netif 'vmnet1' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 13:00:17.999 (   0.004s) [python          ]      netinterfaces.cpp:102   INFO|       IPv4 addr: ac105801
2025-07-03 13:00:17.999 (   0.004s) [python          ]      netinterfaces.cpp:89    INFO| netif 'vmnet8' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 13:00:17.999 (   0.004s) [python          ]      netinterfaces.cpp:102   INFO|       IPv4 addr: c0a8d801
2025-07-03 13:00:17.999 (   0.004s) [python          ]         api_config.cpp:270   INFO| Loaded default config
2025-07-03 13:00:17.999 (   0.005s) [python          ]             common.cpp:65    INFO| git:/branch:HEAD/build:Release/compiler:GNU-13.3.0/link:SHARED
Traceback (most recent call last):
  File "main.py", line 7, in <module>
    emotiv_epoc_x.main_loop()
  File "/home/halechr/repos/emotiv-lsl/emotiv_lsl/emotiv_base.py", line 23, in main_loop
    hid_device = hid.Device(path=device['path'])
  File "/home/halechr/miniforge3/envs/lsl_env/lib/python3.8/site-packages/hid/__init__.py", line 130, in __init__
    raise HIDException('unable to open device')
hid.HIDException: unable to open device
(lsl_env) halechr@RDLU0039:~/repos/emotiv-lsl$ python main.py 
crypto_key: bytearray(b'6566565666756557')
2025-07-03 13:00:20.590 (   0.004s) [python          ]      netinterfaces.cpp:89    INFO| netif 'lo' (status: 1, multicast: 0, broadcast: 0)
2025-07-03 13:00:20.590 (   0.004s) [python          ]      netinterfaces.cpp:89    INFO| netif 'enp2s0' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 13:00:20.590 (   0.004s) [python          ]      netinterfaces.cpp:89    INFO| netif 'enp0s31f6' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 13:00:20.590 (   0.004s) [python          ]      netinterfaces.cpp:89    INFO| netif 'docker0' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 13:00:20.590 (   0.004s) [python          ]      netinterfaces.cpp:89    INFO| netif 'vmnet1' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 13:00:20.590 (   0.004s) [python          ]      netinterfaces.cpp:89    INFO| netif 'vmnet8' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 13:00:20.590 (   0.004s) [python          ]      netinterfaces.cpp:89    INFO| netif 'lo' (status: 1, multicast: 0, broadcast: 0)
2025-07-03 13:00:20.590 (   0.005s) [python          ]      netinterfaces.cpp:89    INFO| netif 'enp0s31f6' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 13:00:20.590 (   0.005s) [python          ]      netinterfaces.cpp:102   INFO|       IPv4 addr: a116954
2025-07-03 13:00:20.590 (   0.005s) [python          ]      netinterfaces.cpp:89    INFO| netif 'docker0' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 13:00:20.590 (   0.005s) [python          ]      netinterfaces.cpp:102   INFO|       IPv4 addr: ac110001
2025-07-03 13:00:20.590 (   0.005s) [python          ]      netinterfaces.cpp:89    INFO| netif 'vmnet1' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 13:00:20.590 (   0.005s) [python          ]      netinterfaces.cpp:102   INFO|       IPv4 addr: ac105801
2025-07-03 13:00:20.590 (   0.005s) [python          ]      netinterfaces.cpp:89    INFO| netif 'vmnet8' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 13:00:20.590 (   0.005s) [python          ]      netinterfaces.cpp:102   INFO|       IPv4 addr: c0a8d801
2025-07-03 13:00:20.590 (   0.005s) [python          ]         api_config.cpp:270   INFO| Loaded default config
2025-07-03 13:00:20.591 (   0.005s) [python          ]             common.cpp:65    INFO| git:/branch:HEAD/build:Release/compiler:GNU-13.3.0/link:SHARED
Traceback (most recent call last):
  File "main.py", line 7, in <module>
    emotiv_epoc_x.main_loop()
  File "/home/halechr/repos/emotiv-lsl/emotiv_lsl/emotiv_base.py", line 23, in main_loop
    hid_device = hid.Device(path=device['path'])
  File "/home/halechr/miniforge3/envs/lsl_env/lib/python3.8/site-packages/hid/__init__.py", line 130, in __init__
    raise HIDException('unable to open device')
hid.HIDException: unable to open device
(lsl_env) halechr@RDLU0039:~/repos/emotiv-lsl$ ls /dev/hid*
/dev/hidraw0  /dev/hidraw1  /dev/hidraw2  /dev/hidraw3  /dev/hidraw4  /dev/hidraw5  /dev/hidraw6
(lsl_env) halechr@RDLU0039:~/repos/emotiv-lsl$ ls /dev/
Display all 332 possibilities? (y or n)
autofs            dm-4              hidraw4           log               loop23            loop39            loop54            loop7             loop-control      nvidia-uvm        rtc0              tty               tty23             tty39             tty54             ttyS10            ttyS26            usb/              vcsa3             vmci
block/            dm-5              hidraw5           loop0             loop24            loop4             loop55            loop70            mapper/           nvidia-uvm-tools  sda               tty0              tty24             tty4              tty55             ttyS11            ttyS27            userfaultfd       vcsa4             vmmon
bsg/              dm-6              hidraw6           loop1             loop25            loop40            loop56            loop71            mcelog            nvme0             sda1              tty1              tty25             tty40             tty56             ttyS12            ttyS28            userio            vcsa5             vmnet0
btrfs-control     dm-7              hpet              loop10            loop26            loop41            loop57            loop72            mei0              nvme0n1           sdb               tty10             tty26             tty41             tty57             ttyS13            ttyS29            vboxdrv           vcsa6             vmnet1
bus/              dm-8              hugepages/        loop11            loop27            loop42            loop58            loop73            mem               nvme0n1p1         sdb1              tty11             tty27             tty42             tty58             ttyS14            ttyS3             vboxdrvu          vcsu              vmnet8
cdrom             dma_heap/         hwrng             loop12            loop28            loop43            loop59            loop74            mqueue/           nvme0n1p2         sg0               tty12             tty28             tty43             tty59             ttyS15            ttyS30            vboxnetctl        vcsu1             vsock
char/             dri/              i2c-0             loop13            loop29            loop44            loop6             loop75            mtd0              nvme0n1p3         sg1               tty13             tty29             tty44             tty6              ttyS16            ttyS31            vboxusb/          vcsu2             wmi/
console           ecryptfs          i2c-1             loop14            loop3             loop45            loop60            loop76            mtd0ro            nvram             sg2               tty14             tty3              tty45             tty60             ttyS17            ttyS4             vcs               vcsu3             zero
core              fb0               i2c-2             loop15            loop30            loop46            loop61            loop77            mtd1              port              shm/              tty15             tty30             tty46             tty61             ttyS18            ttyS5             vcs1              vcsu4             zfs
cpu/              fd/               i2c-3             loop16            loop31            loop47            loop62            loop78            mtd1ro            ppp               snapshot          tty16             tty31             tty47             tty62             ttyS19            ttyS6             vcs2              vcsu5             
cpu_dma_latency   full              i2c-4             loop17            loop32            loop48            loop63            loop79            net/              psaux             snd/              tty17             tty32             tty48             tty63             ttyS2             ttyS7             vcs3              vcsu6             
cuse              fuse              i2c-5             loop18            loop33            loop49            loop64            loop8             ng0n1             ptmx              sr0               tty18             tty33             tty49             tty7              ttyS20            ttyS8             vcs4              vfio/             
disk/             gpiochip0         initctl           loop19            loop34            loop5             loop65            loop80            null              ptp0              stderr            tty19             tty34             tty5              tty8              ttyS21            ttyS9             vcs5              vg0/              
dm-0              hidraw0           input/            loop2             loop35            loop50            loop66            loop81            nvidia0           pts/              stdin             tty2              tty35             tty50             tty9              ttyS22            udmabuf           vcs6              vga_arbiter       
dm-1              hidraw1           isst_interface    loop20            loop36            loop51            loop67            loop82            nvidia-caps/      random            stdout            tty20             tty36             tty51             ttyprintk         ttyS23            uhid              vcsa              vhci              
dm-2              hidraw2           kmsg              loop21            loop37            loop52            loop68            loop83            nvidiactl         rfkill            tpm0              tty21             tty37             tty52             ttyS0             ttyS24            uinput            vcsa1             vhost-net         
dm-3              hidraw3           kvm               loop22            loop38            loop53            loop69            loop9             nvidia-modeset    rtc               tpmrm0            tty22             tty38             tty53             ttyS1             ttyS25            urandom           vcsa2             vhost-vsock       
(lsl_env) halechr@RDLU0039:~/repos/emotiv-lsl$ lsusb
Bus 002 Device 003: ID 05e3:0612 Genesys Logic, Inc. Hub
Bus 002 Device 002: ID 0bda:0411 Realtek Semiconductor Corp. Hub
Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
Bus 001 Device 005: ID 046d:c537 Logitech, Inc. Cordless Mouse Receiver
Bus 001 Device 004: ID 046d:c335 Logitech, Inc. G910 Orion Spectrum Mechanical Keyboard
Bus 001 Device 003: ID 05e3:0610 Genesys Logic, Inc. Hub
Bus 001 Device 009: ID 1234:ed02 Brain Actuated Technologies Emotiv EPOC Developer Headset Wireless Dongle
Bus 001 Device 002: ID 0bda:5411 Realtek Semiconductor Corp. RTS5411 Hub
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub

(lsl_env) halechr@RDLU0039:~/repos/emotiv-lsl$ sudo chmod 0666 /dev/hidraw*
(lsl_env) halechr@RDLU0039:~/repos/emotiv-lsl$ python main.py 
crypto_key: bytearray(b'6566565666756557')
2025-07-03 13:01:46.758 (   0.005s) [python          ]      netinterfaces.cpp:89    INFO| netif 'lo' (status: 1, multicast: 0, broadcast: 0)
2025-07-03 13:01:46.758 (   0.005s) [python          ]      netinterfaces.cpp:89    INFO| netif 'enp2s0' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 13:01:46.758 (   0.005s) [python          ]      netinterfaces.cpp:89    INFO| netif 'enp0s31f6' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 13:01:46.758 (   0.005s) [python          ]      netinterfaces.cpp:89    INFO| netif 'docker0' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 13:01:46.758 (   0.005s) [python          ]      netinterfaces.cpp:89    INFO| netif 'vmnet1' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 13:01:46.758 (   0.005s) [python          ]      netinterfaces.cpp:89    INFO| netif 'vmnet8' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 13:01:46.758 (   0.005s) [python          ]      netinterfaces.cpp:89    INFO| netif 'lo' (status: 1, multicast: 0, broadcast: 0)
2025-07-03 13:01:46.758 (   0.005s) [python          ]      netinterfaces.cpp:89    INFO| netif 'enp0s31f6' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 13:01:46.758 (   0.005s) [python          ]      netinterfaces.cpp:102   INFO|       IPv4 addr: a116954
2025-07-03 13:01:46.758 (   0.005s) [python          ]      netinterfaces.cpp:89    INFO| netif 'docker0' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 13:01:46.758 (   0.005s) [python          ]      netinterfaces.cpp:102   INFO|       IPv4 addr: ac110001
2025-07-03 13:01:46.758 (   0.005s) [python          ]      netinterfaces.cpp:89    INFO| netif 'vmnet1' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 13:01:46.758 (   0.005s) [python          ]      netinterfaces.cpp:102   INFO|       IPv4 addr: ac105801
2025-07-03 13:01:46.758 (   0.005s) [python          ]      netinterfaces.cpp:89    INFO| netif 'vmnet8' (status: 1, multicast: 4096, broadcast: 2)
2025-07-03 13:01:46.758 (   0.005s) [python          ]      netinterfaces.cpp:102   INFO|       IPv4 addr: c0a8d801
2025-07-03 13:01:46.758 (   0.005s) [python          ]         api_config.cpp:270   INFO| Loaded default config
2025-07-03 13:01:46.758 (   0.006s) [python          ]             common.cpp:65    INFO| git:/branch:HEAD/build:Release/compiler:GNU-13.3.0/link:SHARED
```
