import logging
import asyncio
from emotiv_lsl.helpers import HardwareConnectionBackend, CyKitCompatibilityHelpers
from emotiv_lsl.ble_device import BleHidLikeDevice
from emotiv_lsl.emotiv_epoc_x import EmotivEpocX
from emotiv_lsl.emotiv_epoc_plus import EmotivEpocPlus
from emotiv_lsl.emotiv_base import EmotivBase


logger = logging.getLogger(f'emotiv.DiscoverDevices')


ble_device_name_hint_to_class_dict = {
    'EPOCX': EmotivEpocX,
    'EPOC+': EmotivEpocPlus,
    'EPOC': EmotivBase,
}

def find_first_hw_device(backend: HardwareConnectionBackend=HardwareConnectionBackend.BLUETOOTH, is_reverse_engineer_mode: bool=False):
    # raise NotImplementedError(f'Specific hardware class (e.g. Epoc X) must override this to provide a concrete implementation.')
    hw_device = None
    if backend.value == HardwareConnectionBackend.USB.value:
        import hid
        raise NotImplementedError('USB mode not supported yet')
        # device = self.get_hid_device()
        # hw_device = hid.Device(path=device['path'])
        # if is_reverse_engineer_mode:
        #     logger.info(f'hid_device: {hw_device}\n\twith path: {device["path"]}\n')

    elif backend.value == HardwareConnectionBackend.BLUETOOTH.value:
        from emotiv_lsl.ble_device import BleHidLikeDevice
        hw_device = BleHidLikeDevice(device_name_hint='EPOC') ## set to 'EPOC' which will find either Epoc X or Epoc Plus
        logger.info(f'find_first_hw_device(): hw_device: {hw_device}')
        if is_reverse_engineer_mode:
            logger.info(f'hw_device: {hw_device}\n\twith info: {hw_device._device_info_dict}\n')
    else:
        raise NotImplementedError(f'self.backend: {backend.value} not expected!')

    info_dict = hw_device._device_info_dict
    assert info_dict is not None, f'info_dict is None'
    a_name: str = info_dict['name']
    headset_name: str = info_dict['headset_name']
    logger.info(f'a_name: {a_name}\t headset_name: {headset_name}')
    headset_BT_hex_key = info_dict['headset_BT_hex_key']
    # hw_device.ble_device_name_hint = 'EPOC'
    return hw_device
    

async def discover_devices():
    from bleak import BleakScanner

    devices = await BleakScanner.discover()
    for d in devices:
        # 949F7EA5-0829-05F7-3441-7BAABB0F0064: EPOCX (E50202E9)
        # 949F7EA5-0829-05F7-3441-7BAABB0F0064: EPOCX (E50202E9)  info_dict: {'address': '949F7EA5-0829-05F7-3441-7BAABB0F0064', 'name': 'EPOCX (E50202E9)', 'details': (<CBPeripheral: 0x7fb8b300aed0, identifier = 949F7EA5-0829-05F7-3441-7BAABB0F0064, name = EPOCX (E50202E9), mtu = 0, state = disconnected>, <CentralManagerDelegate: 0x7fb8c2869740>)}
        #: The Bluetooth address of the device on this machine (UUID on macOS).
        info_dict = {'address': d.address, 'name': d.name, 'details': d.details}
        a_name: str = d.name
        # print(f'\ta_name: "{a_name}"')
        if (a_name is not None) and a_name.startswith('EPOC'):
            logger.debug(f"found_device with name: '{a_name}'")
            *headset_name_parts, headset_BT_hex_key = a_name.split(' ')
            headset_name = ' '.join(headset_name_parts)
            headset_BT_hex_key = headset_BT_hex_key.strip(')(')
            info_dict['headset_name'] = headset_name
            info_dict['headset_BT_hex_key'] = headset_BT_hex_key
            # Some names include 8 hex digits in parens, e.g. E50202E9
            assert len(headset_BT_hex_key) == 8, f"len(headset_BT_hex_key): {len(headset_BT_hex_key)}, headset_BT_hex_key: '{headset_BT_hex_key}'"
            serial_number = bytes(("\x00" * 12),'utf-8') + bytearray.fromhex(str(headset_BT_hex_key[6:8] + headset_BT_hex_key[4:6] + headset_BT_hex_key[2:4] + headset_BT_hex_key[0:2]))
            info_dict['headset_serial_number'] = serial_number
            # print(f'{d}\tinfo_dict: {info_dict}') 
            logger.info(f"{d}\tinfo_dict: {info_dict}")

            #: The operating system name of the device (not necessarily the local name
            #: from the advertising data), suitable for display to the user.
            # d.name = name
            # : The OS native details required for connecting to the device.
            # d.details = details
            # print(d)
            


# ble_device_name_hint

if __name__ == "__main__":
    # Configure logging for debugging data packets
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger.info("===================== start main_BLE.py =====================")
    logger.info(">>> Searching for headset... connect via BLE or (eventually) USB.")
    a_device = find_first_hw_device(backend=HardwareConnectionBackend.BLUETOOTH)
    logger.info(f'a_device: {a_device}')

    _common_kwargs = {
        'enable_debug_logging': True,
        'is_reverse_engineer_mode': True,
    }

    if a_device._device_info_dict['headset_name'] == 'EPOCX':
        logger.info(">>> Found Hardware: EPOC X")
        hardcoded_epocX_key_kwargs = {
            'ble_device_name_hint': 'EPOCX',
            'serial_number': b'\xe5\x02\x02\x02\x02\x02\x02\xe9\xe5\xe9\x02\x02\xe9\xe9\x02\xe5', # 'E50202E9',
            'cryptokey': b'\xe5\x02\x02\x02\x02\x02\x02\xe9\xe5\xe9\x02\x02\xe9\xe9\x02\xe5',
            'hw_device': a_device,
            **_common_kwargs,
        }
        emotiv_epoc = EmotivEpocX.init_with_serial(**hardcoded_epocX_key_kwargs, backend=HardwareConnectionBackend.BLUETOOTH)
    elif a_device._device_info_dict['headset_name'] == 'EPOC+':
        logger.info(">>> Found Hardware: EPOC+")
        hardcoded_epoc_plus_key_kwargs = {
            'ble_device_name_hint': 'EPOC+',
            'serial_number': b';\x9a\x9a\xcc\xcc\xcc\x9a\xa6;\xa6\x9a\x9a\xa6\xa6\x9a;', #'3B9ACCA6',
            'cryptokey': b';\x9a\x9a\xcc\xcc\xcc\x9a\xa6;\xa6\x9a\x9a\xa6\xa6\x9a;',
            'hw_device': a_device,
            **_common_kwargs,
        }
        emotiv_epoc = EmotivEpocPlus.init_with_serial(**hardcoded_epoc_plus_key_kwargs, backend=HardwareConnectionBackend.BLUETOOTH)
    else:
        logger.error(f'a_device._device_info_dict["headset_name"]: {a_device._device_info_dict["headset_name"]} not expected!')
        raise ValueError(f'a_device._device_info_dict["headset_name"]: {a_device._device_info_dict["headset_name"]} not expected!')


    # logger = logging.getLogger("emotiv_lsl")
    # logger.setLevel(logging.DEBUG)

    # file_handler = logging.FileHandler("logs_and_notes/logs/decode_tracing.log")
    # file_handler.setLevel(logging.WARN)

    # console_handler = logging.StreamHandler()
    # console_handler.setLevel(logging.INFO)

    # formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    # file_handler.setFormatter(formatter)
    # console_handler.setFormatter(formatter)

    # logger.addHandler(file_handler)
    # logger.addHandler(console_handler)

    # logger.info("info → console only")
    # logger.error("error → console + file")

    # logging.basicConfig(filename="logs_and_notes/logs/decode_tracing.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    # asyncio.run(BleHidLikeDevice.discover_devices())
    
    # # crypto_key = emotiv_epoc.get_crypto_key()
    # # print(f'crypto_key: {crypto_key}')

    logger.info("===================== Starting main loop =====================")
    emotiv_epoc.main_loop()
    
    # emotiv_epoc = EmotivEpocX(backend=HardwareConnectionBackend.BLUETOOTH)
    # # crypto_key = emotiv_epoc.get_crypto_key()
    # # print(f'crypto_key: {crypto_key}')
    # emotiv_epoc.main_loop()

    # emotiv_epoc_x = EmotivEpocX(backend=HardwareConnectionBackend.BLUETOOTH)
    # # crypto_key = emotiv_epoc_x.get_crypto_key()
    # # print(f'crypto_key: {crypto_key}')
    # emotiv_epoc_x.main_loop()
    # asyncio.run(BleHidLikeDevice.discover_devices())
