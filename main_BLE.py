import logging
import asyncio
from emotiv_lsl.helpers import HardwareConnectionBackend, CyKitCompatibilityHelpers
from emotiv_lsl.ble_device import BleHidLikeDevice
from emotiv_lsl.emotiv_epoc_x import EmotivEpocX
from emotiv_lsl.emotiv_epoc_plus import EmotivEpocPlus


if __name__ == "__main__":
    # Configure logging for debugging data packets
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
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

    hardcoded_epoc_plus_key_kwargs = {
        'ble_device_name_hint': 'EPOC+',
        'serial_number': b';\x9a\x9a\xcc\xcc\xcc\x9a\xa6;\xa6\x9a\x9a\xa6\xa6\x9a;', #'3B9ACCA6',
        'cryptokey': b';\x9a\x9a\xcc\xcc\xcc\x9a\xa6;\xa6\x9a\x9a\xa6\xa6\x9a;',
    }
    emotiv_epoc = EmotivEpocPlus.init_with_serial(**hardcoded_epoc_plus_key_kwargs, backend=HardwareConnectionBackend.BLUETOOTH)
    

    # hardcoded_epocX_key_kwargs = {
    #     'ble_device_name_hint': 'EPOCX',
    #     'serial_number': b'\xe5\x02\x02\x02\x02\x02\x02\xe9\xe5\xe9\x02\x02\xe9\xe9\x02\xe5', # 'E50202E9',
    #     'cryptokey': b'\xe5\x02\x02\x02\x02\x02\x02\xe9\xe5\xe9\x02\x02\xe9\xe9\x02\xe5',
    # }
    # emotiv_epoc = EmotivEpocX.init_with_serial(**hardcoded_epocX_key_kwargs, backend=HardwareConnectionBackend.BLUETOOTH)
    # emotiv_epoc = EmotivEpocPlus(backend=HardwareConnectionBackend.BLUETOOTH)
    
    
    # crypto_key = emotiv_epoc.get_crypto_key()
    # print(f'crypto_key: {crypto_key}')
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
