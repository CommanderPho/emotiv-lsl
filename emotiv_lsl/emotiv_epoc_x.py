import hid
import logging
from Crypto.Cipher import AES
from typing import Dict, List, Tuple, Optional, Callable, Union, Any
from nptyping import NDArray
from pylsl import StreamInfo
from attrs import define, field, Factory

from emotiv_lsl.emotiv_base import EmotivBase
from config import MOTION_SRATE, SRATE

@define(slots=False)
class EmotivEpocX(EmotivBase):
    READ_SIZE: int = field(default=32)
    device_name: str = field(default='Emotiv Epoc X')
    KeyModel: int = field(default = 8) # call Epoc X keymodel 8 to extend CyKit's keymodel system
    
    is_reverse_engineer_mode: bool = field(default=False)
    
    
    def __attrs_post_init__(self):
        self.cipher = AES.new(self.get_crypto_key(), AES.MODE_ECB)
        if self.is_reverse_engineer_mode:
            print('starting with reverse engineer mode!')
            # self.READ_SIZE = 64
                           

    def get_hid_device(self):
        for device in hid.enumerate():
            if (device.get('manufacturer_string', '') == 'Emotiv') and ((device.get('usage', 0) == 2 or device.get('usage', 0) == 0 and device.get('interface_number', 0) == 1)):
                return device
        raise Exception('Emotiv Epoc X not found')

    def get_crypto_key(self) -> bytearray:
        serial = self.get_hid_device()['serial_number']
        self.serial_number = serial
        sn = bytearray()
        for i in range(0, len(serial)):
            sn += bytearray([ord(serial[i])])
        return bytearray([sn[-1], sn[-2], sn[-4], sn[-4], sn[-2], sn[-1], sn[-2], sn[-4], sn[-1], sn[-4], sn[-3], sn[-2], sn[-1], sn[-2], sn[-2], sn[-3]])

    def get_lsl_outlet_motion_stream_info(self) -> StreamInfo:
        """Create LSL stream info for motion sensor data (accelerometer + gyroscope)"""
        ch_names = ['AccX', 'AccY', 'AccZ', 'GyroX', 'GyroY', 'GyroZ']
        n_channels = len(ch_names)
        
        info = StreamInfo('Epoc X Motion', 'SIGNAL', n_channels, MOTION_SRATE, 'float32') ## Use the generic "SIGNAL" type to so that it works with the default `bsl_stream_viewer`
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

        info = StreamInfo('Epoc X', 'EEG', n_channels, SRATE, 'float32')
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

        info = StreamInfo('Epoc X eQuality', type="Raw", channel_count=n_channels, nominal_srate=SRATE, channel_format='float32', source_id=f"{self.device_name}_{self.KeyModel}_{self.get_crypto_key()}")
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
        data = [el ^ 0x55 for el in data]
        data = self.cipher.decrypt(bytearray(data))
        
        # Check for motion/gyro packet
        if str(data[1]) == "32":
            if self.enable_debug_logging:
                logging.getLogger('emotiv.epoc_x').debug(f"Motion/gyro packet detected: data[1]={data[1]}")
            return self.decode_motion_data(data), None ## no `eeg_quality_data` for motion packets

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
            packet_data = packet_data + \
                str(self.convertEPOC_PLUS(str(data[i]), str(data[i+1]))) + self.delimiter

        for i in range(18, len(data), 2):
            packet_data = packet_data + \
                str(self.convertEPOC_PLUS(str(data[i]), str(data[i+1]))) + self.delimiter

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
