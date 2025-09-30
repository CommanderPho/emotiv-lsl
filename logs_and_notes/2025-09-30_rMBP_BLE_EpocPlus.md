(lsl_env) PS C:\Users\pho\repos\EmotivEpoc\emotiv-lsl> python .\main_BLE.py
2025-09-30 12:05:50,873 - emotiv_lsl.ble_device - INFO - found device: {'address': 'C7:52:C2:63:6A:84', 'name': 'EPOC+ (3B9ACCA6)', 'details': _RawAdvData(adv=<_bleak_winrt_Windows_Devices_Bluetooth_Advertisement.BluetoothLEAdvertisementReceivedEventArgs object at 0x000001BB7E71ED50>, scan=None), 'headset_name': 'EPOC+', 'headset_BT_hex_key': '3B9ACCA6', 'headset_serial_number': b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xa6\xcc\x9a;'}
2025-09-30 12:05:50,873 - emotiv_lsl.ble_device - INFO - done enumerating devices found_dev: C7:52:C2:63:6A:84: EPOC+ (3B9ACCA6)        info_dict: {'address': 'C7:52:C2:63:6A:84', 'name': 'EPOC+ (3B9ACCA6)', 'details': _RawAdvData(adv=<_bleak_winrt_Windows_Devices_Bluetooth_Advertisement.BluetoothLEAdvertisementReceivedEventArgs object at 0x000001BB7E71ED50>, scan=None), 'headset_name': 'EPOC+', 'headset_BT_hex_key': '3B9ACCA6', 'headset_serial_number': b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xa6\xcc\x9a;'}
2025-09-30 12:05:50,877 - emotiv_lsl.ble_device - INFO - found_device, connecting...
2025-09-30 12:05:53,474 - emotiv_lsl.ble_device - INFO - Connected to C7:52:C2:63:6A:84: EPOC+ (3B9ACCA6)       info_dict: {'address': 'C7:52:C2:63:6A:84', 'name': 'EPOC+ (3B9ACCA6)', 'details': _RawAdvData(adv=<_bleak_winrt_Windows_Devices_Bluetooth_Advertisement.BluetoothLEAdvertisementReceivedEventArgs object at 0x000001BB7E71ED50>, scan=None), 'headset_name': 'EPOC+', 'headset_BT_hex_key': '3B9ACCA6', 'headset_serial_number': b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xa6\xcc\x9a;'}
2025-09-30 12:05:53,500 - emotiv_lsl.ble_device - INFO - BleHidLikeDevice._init(): FULLY READY!
2025-09-30 12:05:53,500 - emotiv.EmotivBase - INFO - EmotivEpocBase.get_hw_device(): hw_device: <emotiv_lsl.ble_device.BleHidLikeDevice object at 0x000001BB7DD4B850>
BLE Bluetooth mode!
2025-09-30 12:05:53,502 - emotiv.emotiv_epoc+ - INFO - EmotivEpocBase.main_loop(): hw_device: <emotiv_lsl.ble_device.BleHidLikeDevice object at 0x000001BB7DD4B850>  
Traceback (most recent call last):
  File ".\main_BLE.py", line 43, in <module>
    emotiv_epoc.main_loop()
  File "C:\Users\pho\repos\EmotivEpoc\emotiv-lsl\emotiv_lsl\emotiv_base.py", line 257, in main_loop
    decoded, eeg_quality_data = self.decode_data(data)
  File "C:\Users\pho\repos\EmotivEpoc\emotiv-lsl\emotiv_lsl\emotiv_epoc_plus.py", line 126, in decode_data      
    data = self.cipher.decrypt(bytes(join_data,'latin-1')[0:32])
  File "C:\Users\pho\micromamba\envs\lsl_env\lib\site-packages\Crypto\Cipher\_mode_ecb.py", line 196, in decrypt
    raise ValueError("Data must be aligned to block boundary in ECB mode")
ValueError: Data must be aligned to block boundary in ECB mode


# From CyKit:
  Cipher Key = b';\x9a\x9a\xcc\xcc\xcc\x9a\xa6;\xa6\x9a\x9a\xa6\xa6\x9a;'

# From emotiv_lsl (mine):
'headset_BT_hex_key': '3B9ACCA6', 'headset_serial_number': b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xa6\xcc\x9a;'

