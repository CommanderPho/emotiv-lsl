
import logging
from Crypto.Cipher import AES
from typing import Dict, List, Tuple, Optional, Callable, Union, Any
# from nptyping import NDArray
from pylsl import StreamInfo, StreamOutlet
from attrs import define, field, Factory

from emotiv_lsl.helpers import HardwareConnectionBackend, CyKitCompatibilityHelpers
from emotiv_lsl.emotiv_base import EmotivBase

from config import MOTION_SRATE, SRATE


logger = logging.getLogger("emotiv_lsl")

@define(slots=False)
class EmotivEpocX(EmotivBase):
    READ_SIZE: int = field(default=32)
    device_name: str = field(default='Emotiv Epoc X')
    KeyModel: int = field(default = 8) # call Epoc X keymodel 8 to extend CyKit's keymodel system
    ble_device_name_hint: str = field(default='EPOCX')
    
    is_reverse_engineer_mode: bool = field(default=False)
    
    
    def __attrs_post_init__(self):
        if (self.cipher is None):           
            crypto_key = self.get_crypto_key()
            self.cipher = AES.new(crypto_key, AES.MODE_ECB)
        else:
            logger.info(f'working cipher was provided on startup!')

        if self.is_reverse_engineer_mode:
            logger.info('starting with reverse engineer mode!')
            # self.READ_SIZE = 64


    def get_hid_device(self):
        import hid
        for device in hid.enumerate():
            if (device.get('manufacturer_string', '') == 'Emotiv') and ((device.get('usage', 0) == 2 or device.get('usage', 0) == 0 and device.get('interface_number', 0) == 1)):
                return device
        raise Exception('Emotiv Epoc X not found')


    # def get_hw_device(self):
    #     if self.hw_device is not None:
    #         return self.hw_device

    #     hw_device = None
    #     if self.backend.value == HardwareConnectionBackend.USB.value:
    #         import hid
    #         device = self.get_hid_device()
    #         hw_device = hid.Device(path=device['path'])
    #         if self.is_reverse_engineer_mode:
    #             logger.debug(f'hid_device: {hw_device}\n\twith path: {device["path"]}\n')

    #     elif self.backend.value == HardwareConnectionBackend.BLUETOOTH.value:
    #         from emotiv_lsl.ble_device import BleHidLikeDevice
    #         ble_device_name_hint: str = 'EPOCX'
    #         hw_device = BleHidLikeDevice(device_name_hint=ble_device_name_hint)
    #         logger.info(f'EmotivEpocX.get_hw_device(): hw_device: {hw_device}')
    #         if self.is_reverse_engineer_mode:
    #             logger.debug(f'hw_device: {hw_device}\n\twith info: {hw_device._device_info_dict}\n')

    #     else:
    #         raise NotImplementedError(f'self.backend: {self.backend.value} not expected!')

    #     ## Cache the current hardware device, especially important for the BLE device
    #     self.hw_device = hw_device
        
    #     return hw_device
    

    def get_crypto_key(self) -> bytearray:
        if (self.serial_number is None):
            hw_device = self.get_hw_device()
            if hw_device is not None:
                if self.backend.value == HardwareConnectionBackend.USB.value:
                    serial = self.get_hid_device()['serial_number']
                    self.serial_number = serial
                    sn = bytearray()
                    for i in range(0, len(serial)):
                        sn += bytearray([ord(serial[i])])
                    return bytearray([sn[-1], sn[-2], sn[-4], sn[-4], sn[-2], sn[-1], sn[-2], sn[-4], sn[-1], sn[-4], sn[-3], sn[-2], sn[-1], sn[-2], sn[-2], sn[-3]])

                elif self.backend.value == HardwareConnectionBackend.BLUETOOTH.value:
                    serial = hw_device.serial_number
                    k, samplingRate, channels = CyKitCompatibilityHelpers.get_sn(model=self.KeyModel, serial_number=serial, a_backend=self.backend)
                    logging.info(f'BLE HARDWARE MODE: serial: "{serial}", k: "{k}"')
                    return k ## cryptokey
                else:
                    logger.warning(f'self.backend.value: {self.backend.value} unexpected!')
                    return None

        else:
            if isinstance(self.serial_number, bytearray):
                ## serial is actually bytearray
                return self.serial_number
            else:
                serial = self.serial_number

        sn = bytearray()
        for i in range(0, len(serial)):
            sn += bytearray([ord(serial[i])])
        return bytearray([sn[-1], sn[-2], sn[-4], sn[-4], sn[-2], sn[-1], sn[-2], sn[-4], sn[-1], sn[-4], sn[-3], sn[-2], sn[-1], sn[-2], sn[-2], sn[-3]])


    def get_lsl_source_id(self) -> str:
        # source_id: str = self.get_crypto_key().hex() ## convert from bytearray into a hex string
        source_id: str = self.serial_number.hex() ## convert from bytearray into a hex string
        return f"{self.device_name}_{self.KeyModel}_{source_id}"
    

    def get_lsl_outlet_motion_stream_info(self) -> StreamInfo:
        """Create LSL stream info for motion sensor data (accelerometer + gyroscope)"""
        ch_names = ['AccX', 'AccY', 'AccZ', 'GyroX', 'GyroY', 'GyroZ']
        n_channels = len(ch_names)
        
        info = StreamInfo('Epoc X Motion', type='SIGNAL', channel_count=n_channels, nominal_srate=MOTION_SRATE, channel_format='float32', source_id=self.get_lsl_source_id()) ## Use the generic "SIGNAL" type to so that it works with the default `bsl_stream_viewer`
        chns = info.desc().append_child("channels")
        
        # Add accelerometer channels
        for i, label in enumerate(ch_names[:3]):
            ch = chns.append_child("channel")
            ch.append_child_value("label", label)
            ch.append_child_value("unit", "g")
            ch.append_child_value("type", "ACC")
            ch.append_child_value("scaling_factor", "1")
            
        # Add gyroscope channels
        for i, label in enumerate(ch_names[3:]):
            ch = chns.append_child("channel")
            ch.append_child_value("label", label)
            ch.append_child_value("unit", "deg/s")
            ch.append_child_value("type", "GYRO")
            ch.append_child_value("scaling_factor", "1")
            
        return info

    def get_lsl_outlet_eeg_stream_info(self) -> StreamInfo:
        ch_names = self.eeg_channel_names # ['AF3', 'F7', 'F3', 'FC5', 'T7', 'P7', 'O1', 'O2', 'P8', 'T8', 'FC6', 'F4', 'F8', 'AF4']
        n_channels = len(ch_names)

        info = StreamInfo('Epoc X', type='EEG', channel_count=n_channels, nominal_srate=SRATE, channel_format='float32', source_id=self.get_lsl_source_id())
        chns = info.desc().append_child("channels")
        for label in ch_names:
            ch = chns.append_child("channel")
            ch.append_child_value("label", label)
            ch.append_child_value("unit", "microvolts")
            ch.append_child_value("type", "EEG")
            ch.append_child_value("scaling_factor", "1")

        cap = info.desc().append_child("cap")
        cap.append_child_value("name", "easycap-M1")
        cap.append_child_value("labelscheme", "10-20")

        return info

    def get_lsl_outlet_electrode_quality_stream_info(self) -> StreamInfo:
        """ Create LSL stream for EEG sensor quality data. Only active if `self.enable_electrode_quality_stream` is True """
        ch_names = self.eeg_quality_channel_names # [f'q{a_name}' for a_name in ch_names] ## add the 'q' prefix, like ['qAF3', 'qF7', ...]
        n_channels = len(ch_names)

        info = StreamInfo('Epoc X eQuality', type="Raw", channel_count=n_channels, nominal_srate=SRATE, channel_format='float32', source_id=self.get_lsl_source_id())
        chns = info.desc().append_child("channels")
        for label in ch_names:
            ch = chns.append_child("channel")
            ch.append_child_value("label", label)
            ch.append_child_value("unit", "microvolts")
            ch.append_child_value("type", "RAW")
            ch.append_child_value("scaling_factor", "1")

        cap = info.desc().append_child("cap")
        cap.append_child_value("name", "easycap-M1")
        cap.append_child_value("labelscheme", "10-20")

        return info
    

    def decode_data(self, data) -> Tuple[List, Optional[List]]:
        """ 
        From `CyKit/Examples/example_epoc_plus.py`
            join_data = ''.join(map(chr, data[1:]))
            data = self.cipher.decrypt(bytes(join_data,'latin-1')[0:32])
            if str(data[1]) == "32": # No Gyro Data.
                return

        """
        if (self.enable_debug_logging and self.is_reverse_engineer_mode):
            logging.debug(f'decode_data(data: {data})') # find/replace with `.+ - emotiv_lsl - WARNING - (b['"].+['"])` and `$1`
            # logger.warning(f'decode_data(data: {data})')
            logger.warning(f'{data}')
            
        data = [el ^ 0x55 for el in data]
        data = self.cipher.decrypt(bytearray(data))
        
        ## Check for quality values
        eeg_quality_data = None
        if self.enable_electrode_quality_stream:
            try:
                eeg_quality_data = self.extractQualityValues(data=data, return_as_array=True)

            except Exception as e:
                print(f'getting EEG sensor quality values failed with error: {e}')
                eeg_quality_data = None
                pass
                # raise e
            

        packet_data = ""
        for i in range(2, 16, 2):
            packet_data = packet_data + str(self.convertEPOC_PLUS(str(data[i]), str(data[i+1]))) + self.delimiter

        for i in range(18, len(data), 2):
            packet_data = packet_data + str(self.convertEPOC_PLUS(str(data[i]), str(data[i+1]))) + self.delimiter

        packet_data = packet_data[:-len(self.delimiter)]  # Remove extra delimiter.
        packet_data = packet_data.split(self.delimiter)
        packet_data = [float(i) for i in packet_data]

        # swap positions of AF3 and F3
        packet_data[0], packet_data[2] = packet_data[2], packet_data[0]

        # swap positions of AF4 and F4
        packet_data[13], packet_data[11] = packet_data[11], packet_data[13]

        # swap positions of F7 and FC5
        packet_data[1], packet_data[3] = packet_data[3], packet_data[1]

        # swap positions of FC6 and F8
        packet_data[10], packet_data[12] = packet_data[12], packet_data[10]

        return packet_data, eeg_quality_data


    def decode_motion_data(self, data) -> list:
        """Decode motion sensor data from gyro/accelerometer packet
        
        Based on CyKit's convertEPOC_PLUS_gyro function and EPOC X IMU (ICM-20948)
        Returns [AccX, AccY, AccZ, GyroX, GyroY, GyroZ]
        """
        # Motion data positions in EPOC X packet (based on CyKit gyroDATA)
        motion_positions = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 30, 31]
        
        motion_data = []
        for i in range(0, len(motion_positions), 2):
            if i + 1 < len(motion_positions):
                pos1 = motion_positions[i]
                pos2 = motion_positions[i + 1]
                if pos1 < len(data) and pos2 < len(data):
                    # Use EPOC+ gyro conversion formula from CyKit
                    value = ((8191.88296790168 + (data[pos1] * 1.00343814821)) +  ((data[pos2] - 128.00001) * 64.00318037383))
                    motion_data.append(value)
        
        # Return first 6 values as [AccX, AccY, AccZ, GyroX, GyroY, GyroZ]
        # Scale to appropriate units (g for accelerometer, deg/s for gyro)
        if len(motion_data) >= 6:
            # Apply scaling factors based on ICM-20948 specs
            acc_scale = 1.0 / 16384.0  # ±2g range
            gyro_scale = 1.0 / 131.0   # ±250 deg/s range
            self.has_motion_data = True ## indicate we got motion data    
            return [
                motion_data[0] * acc_scale,  # AccX
                motion_data[1] * acc_scale,  # AccY  
                motion_data[2] * acc_scale,  # AccZ
                motion_data[3] * gyro_scale, # GyroX
                motion_data[4] * gyro_scale, # GyroY
                motion_data[5] * gyro_scale  # GyroZ
            ]
        
        return [0.0] * 6  # Return zeros if not enough data

    def validate_data(self, data) -> bool:
        if self.is_reverse_engineer_mode:
            return (len(data) == self.READ_SIZE)
        else:
            return len(data) == 32

    # ---------------- BLE-specific helpers & loop ----------------
    def _decode_eeg_ble(self, payload: list) -> Tuple[Optional[List[float]], Optional[List[float]]]:
        """Decode EEG from BLE DATA_UUID notification payload."""
        if not payload:
            return None, None
        return self.decode_data(payload)

    def _decode_mems_ble(self, payload: list) -> Optional[List[float]]:
        """Decode MEMS from BLE MEMS_UUID notification payload."""
        if not payload:
            return None
        # EPOC X BLE MEMS frames appear to be clear-text on some firmware; decrypt conditionally
        data = payload
        try:
            # Try decrypt path; if sizes mismatch or nonsense, fall back
            tmp = [el ^ 0x55 for el in payload]
            tmp = self.cipher.decrypt(bytearray(tmp))
            if len(tmp) >= 32:
                data = list(tmp)
        except Exception:
            pass
        return self.decode_motion_data(data)

    def main_loop(self):
        """Override for BLE to read EEG and MEMS from separate queues; fallback to base for USB."""
        if self.backend.value != HardwareConnectionBackend.BLUETOOTH.value:
            return super().main_loop()

        logger = logging.getLogger(f'emotiv.{self.device_name.replace(" ", "_").lower()}')
        logger.info('BLE Bluetooth mode (Epoc X) with separate EEG/MEMS streams')

        eeg_outlet = None
        motion_outlet = None
        raw_packet_outlet = None
        eeg_quality_outlet = None

        if self.is_reverse_engineer_mode:
            raw_packet_outlet = StreamOutlet(self.get_lsl_outlet_raw_debugging_stream_info())
            logger.info('Setup raw_packet_outlet (for reverse-engineering)')

        hw_device = self.get_hw_device()
        assert hw_device is not None

        eeg_count = 0
        mems_count = 0
        debug_frames = 10 if self.enable_debug_logging else 0

        while True:
            eeg_payload = hw_device.read_data(self.READ_SIZE, timeout_ms=10)
            if eeg_payload:
                eeg_count += 1
                if raw_packet_outlet is not None:
                    raw_packet_outlet.push_sample(eeg_payload)
                if debug_frames > 0 and self.is_reverse_engineer_mode:
                    logger.info(f'EEG[{eeg_count}]: {bytes(eeg_payload).hex()}')
                    debug_frames -= 1
                decoded, eeg_quality_data = self._decode_eeg_ble(eeg_payload)
                if decoded is not None:
                    if eeg_outlet is None:
                        eeg_outlet = StreamOutlet(self.get_lsl_outlet_eeg_stream_info())
                        logger.info('set up EEG outlet!')
                    eeg_outlet.push_sample(decoded)
                if (eeg_quality_data is not None) and len(eeg_quality_data) == 14:
                    if eeg_quality_outlet is None:
                        eeg_quality_outlet = StreamOutlet(self.get_lsl_outlet_electrode_quality_stream_info())
                        logger.info('set up EEG Sensor Quality outlet!')
                    eeg_quality_outlet.push_sample(eeg_quality_data)

            mems_payload = hw_device.read_mems(self.READ_SIZE, timeout_ms=5)
            if mems_payload:
                mems_count += 1
                if debug_frames > 0 and self.is_reverse_engineer_mode:
                    logger.info(f'MEMS[{mems_count}]: {bytes(mems_payload).hex()}')
                    debug_frames -= 1
                motion = self._decode_mems_ble(mems_payload)
                if motion is not None and len(motion) == 6:
                    if not self.has_motion_data:
                        self.has_motion_data = True
                        logger.info('got first motion data!')
                    if motion_outlet is None:
                        motion_outlet = StreamOutlet(self.get_lsl_outlet_motion_stream_info())
                        logger.info('set up motion outlet!')
                    motion_outlet.push_sample(motion)
