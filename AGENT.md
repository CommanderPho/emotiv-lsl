# AGENT.md - Emotiv-LSL Project

## Build/Run/Test Commands
- **Run main LSL server**: `python main.py`
- **Install dependencies**: `pip install -r requirements.txt` or `pip install -r requirements_for_mamba.txt`
- **Setup conda env**: `conda create -n lsl_env python=3.8 && conda activate lsl_env && conda install -c conda-forge liblsl`
- **View LSL stream**: `bsl_stream_viewer` (after installing bsl)
- **Run examples**: `python examples/read_data.py` or `python examples/pho_read_and_export_mne.py`
- **No formal tests**: Project uses manual testing with hardware

## Architecture
- **Main entry**: `main.py` instantiates EmotivEpocX and runs main_loop()
- **Core module**: `emotiv_lsl/` contains device classes (EmotivEpocX, EmotivEpocPlus, EmotivBase)
- **Examples**: `examples/` has data reading, MNE export, and analysis notebooks
- **LSL streaming**: Uses pylsl to stream EEG data from Emotiv headsets
- **Encryption**: AES decryption using device serial-based crypto keys
- **Dependencies**: Python 3.8+, hidapi, pycryptodome, pylsl, mne, matplotlib

## Code Style
- **Imports**: Standard library first, then third-party (hid, pylsl, Crypto), then local imports
- **Classes**: CamelCase (EmotivEpocX), inherit from EmotivBase
- **Methods**: snake_case (get_crypto_key, main_loop)  
- **Constants**: UPPER_CASE (SRATE in config.py)
- **Error handling**: Raise exceptions with descriptive messages
- **Type hints**: Use -> return type annotations where present
