import logging
import asyncio
from emotiv_lsl.helpers import HardwareConnectionBackend, CyKitCompatibilityHelpers
from emotiv_lsl.ble_device import BleHidLikeDevice
from emotiv_lsl.emotiv_epoc_x import EmotivEpocX



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
    

    emotiv_epoc_x = EmotivEpocX(backend=HardwareConnectionBackend.BLUETOOTH)
    crypto_key = emotiv_epoc_x.get_crypto_key()
    print(f'crypto_key: {crypto_key}')
    emotiv_epoc_x.main_loop()
    # asyncio.run(BleHidLikeDevice.discover_devices())
