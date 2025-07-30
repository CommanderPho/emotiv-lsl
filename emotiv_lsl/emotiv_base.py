from typing import Any
import hid
import logging
from pylsl import StreamInfo, StreamOutlet
from attrs import define, field, Factory

@define(slots=False)
class EmotivBase():
    READ_SIZE: int = field(default=32)
    serial_number: str = field(default=None)
    device_name: str = field(default='UnknownEmotivHeadset')
    delimiter: str = field(default=',')
    cipher: Any = field(init=False)
    
    # def __attrs_post_init__(self):
    #     self.cipher = Cipher(self.serial_number)

    def get_hid_device(self):
        for device in hid.enumerate():
            if device.get('manufacturer_string', '') == 'Emotiv' and ((device.get('usage', 0) == 2 or device.get('usage', 0) == 0 and device.get('interface_number', 0) == 1)):
                return device
        raise Exception('Emotiv Epoc Base Headset not found')
    
    def get_crypto_key(self) -> bytearray:
        raise NotImplementedError(
            'get_crypto_key method must be implemented in subclass')


    def get_hid_device(self):
        pass

    def get_stream_info(self) -> StreamInfo:
        pass

    def decode_data(self) -> list:
        pass

    def validate_data(self, data) -> bool:
        pass

    def main_loop(self):
        # Create EEG outlet
        eeg_outlet = StreamOutlet(self.get_stream_info())
        
        # Create motion outlet if the device supports it
        motion_outlet = None
        if hasattr(self, 'get_motion_stream_info'):
            motion_outlet = StreamOutlet(self.get_motion_stream_info())
        
        device = self.get_hid_device()
        hid_device = hid.Device(path=device['path'])
        
        logger = logging.getLogger(f'emotiv.{self.device_name.replace(" ", "_").lower()}')
        packet_count = 0
        
        while True:
            data = hid_device.read(self.READ_SIZE)
            packet_count += 1
            
            if self.validate_data(data):
                logger.debug(f"Packet #{packet_count}: Valid data packet, length={len(data)}")
                decoded = self.decode_data(data)
                if decoded is not None:
                    # Check if this is motion data (based on number of channels)
                    if len(decoded) == 6 and motion_outlet is not None:
                        logger.debug(f"Packet #{packet_count}: Motion data decoded, {len(decoded)} channels")
                        motion_outlet.push_sample(decoded)
                    elif len(decoded) == 14:  # EEG data has 14 channels
                        logger.debug(f"Packet #{packet_count}: EEG data decoded, {len(decoded)} channels")
                        eeg_outlet.push_sample(decoded)
                    else:
                        logger.debug(f"Packet #{packet_count}: Unknown data type with {len(decoded)} channels")
                else:
                    logger.debug(f"Packet #{packet_count}: Motion/gyro data packet (skipped)")
            else:
                logger.debug(f"Packet #{packet_count}: Invalid data packet, length={len(data)}")