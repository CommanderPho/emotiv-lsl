from typing import Any
import hid
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
        outlet = StreamOutlet(self.get_stream_info())
        device = self.get_hid_device()
        hid_device = hid.Device(path=device['path'])
        while True:
            data = hid_device.read(self.READ_SIZE)
            if self.validate_data(data):
                decoded = self.decode_data(data)
                outlet.push_sample(decoded)