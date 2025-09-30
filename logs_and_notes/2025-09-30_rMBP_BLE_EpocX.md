2025-09-30 11:28:29,886 - emotiv_lsl.ble_device - INFO - done enumerating devices found_dev: 949F7EA5-0829-05F7-3441-7BAABB0F0064: EPOCX (E50202E9)     info_dict: {'address': '949F7EA5-0829-05F7-3441-7BAABB0F0064', 'name': 'EPOCX (E50202E9)', 'details': (<CBPeripheral: 0x7fe4c1979ed0, identifier = 949F7EA5-0829-05F7-3441-7BAABB0F0064, name = EPOCX (E50202E9), mtu = 0, state = disconnected>, <CentralManagerDelegate: 0x7fe4c19306a0>), 'headset_name': 'EPOCX', 'headset_BT_hex_key': 'E50202E9', 'headset_serial_number': b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe9\x02\x02\xe5'}
2025-09-30 11:28:29,895 - emotiv_lsl.ble_device - INFO - found_device, connecting...
2025-09-30 11:28:30,998 - emotiv_lsl.ble_device - INFO - Connected to 949F7EA5-0829-05F7-3441-7BAABB0F0064: EPOCX (E50202E9)    info_dict: {'address': '949F7EA5-0829-05F7-3441-7BAABB0F0064', 'name': 'EPOCX (E50202E9)', 'details': (<CBPeripheral: 0x7fe4c1979ed0, identifier = 949F7EA5-0829-05F7-3441-7BAABB0F0064, name = EPOCX (E50202E9), mtu = 87, state = connected>, <CentralManagerDelegate: 0x7fe4c19306a0>), 'headset_name': 'EPOCX', 'headset_BT_hex_key': 'E50202E9', 'headset_serial_number': b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe9\x02\x02\xe5'}
2025-09-30 11:28:31,028 - emotiv_lsl.ble_device - INFO - BleHidLikeDevice._init(): FULLY READY!
2025-09-30 11:28:31,028 - emotiv_lsl - INFO - EmotivEpocX.get_hw_device(): hw_device: <emotiv_lsl.ble_device.BleHidLikeDevice object at 0x11124d490>
BLE Bluetooth mode!
2025-09-30 11:28:31,035 - emotiv.emotiv_epoc_x - INFO - EmotivEpocBase.main_loop(): hw_device: <emotiv_lsl.ble_device.BleHidLikeDevice object at 0x11124d490>




# From CyKit:  
	 Cipher Key = b'\xe5\x02\x02\x02\x02\x02\x02\xe9\xe5\xe9\x02\x02\xe9\xe9\x02\xe5'

# From emotiv_lsl (mine):
	'headset_BT_hex_key': 'E50202E9', 'headset_serial_number': b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe9\x02\x02\xe5'
