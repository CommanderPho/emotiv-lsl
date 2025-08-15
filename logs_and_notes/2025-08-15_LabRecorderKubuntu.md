
## Installing on Lab Kubuntu
```bash
cd ~/Downloads
curl -L https://github.com/sccn/liblsl/releases/download/v1.16.4/liblsl-1.16.4-jammy_amd64.deb -o liblsl.deb
sudo dpkg -i liblsl.deb 
sudo dpkg -i ~/Downloads/LabRecorder-1.16.4-jammy_amd64.deb
sudo dpkg -L LabRecorder
```

## Running

```bash

/usr/bin/LabRecorder

```