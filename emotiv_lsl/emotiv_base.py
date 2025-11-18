from typing import Dict, List, Tuple, Optional, Callable, Union, Any
from datetime import datetime, timedelta
# import hid
import asyncio
import logging
from Crypto.Cipher import AES
import numpy as np
from nptyping import NDArray
import pylsl
from pylsl import StreamInfo, StreamOutlet
from attrs import define, field, Factory
from phopylslhelper.easy_time_sync import EasyTimeSyncParsingMixin, readable_dt_str, from_readable_dt_str


@define(slots=False)
class EmotivBase(EasyTimeSyncParsingMixin):
    READ_SIZE: int = field(default=32)
    serial_number: str = field(default=None)
    device_name: str = field(default='UnknownEmotivHeadset')
    delimiter: str = field(default=',')
    cipher: Any = field(default=None)
    KeyModel: int = field(default = 1)    
    
    # Connection abstraction fields
    connection: Any = field(default=None)  # EmotivConnectionBase instance
    connection_type: str = field(default='usb')  # 'usb', 'ble', or 'auto'
    connection_config: dict = field(factory=dict)  # Connection-specific configuration
    
    has_motion_data: bool = field(default=False)
    enable_debug_logging: bool = field(default=False)
    is_reverse_engineer_mode: bool = field(default=False)
    enable_electrode_quality_stream: bool = field(default=True)

    # def __attrs_post_init__(self):
    #     self.cipher = Cipher(self.serial_number)
    

    @property
    def eeg_channel_names(self) -> List[str]:
        """The eeg_channel_names property."""
        return ['AF3', 'F7', 'F3', 'FC5', 'T7', 'P7', 'O1', 'O2', 'P8', 'T8', 'FC6', 'F4', 'F8', 'AF4']

    @property
    def eeg_quality_channel_names(self) -> List[str]:
        """The eeg_quality_channel_names property."""
        return [f'q{a_name}' for a_name in self.eeg_channel_names] ## add the 'q' prefix, like ['qAF3', 'qF7', ...]
        

    @classmethod
    def init_with_serial(cls, serial_number: str, cryptokey: Optional[bytearray]=None, **kwargs):
        """ doesn't require `hid` or USB access, makes the object with an explicit key """
        # bytearray(b'6566565666756557')        
        if cryptokey is not None:
            cipher = AES.new(cryptokey, AES.MODE_ECB)
            _obj = cls(cipher=cipher, **kwargs) # , cryptokey=cryptokey
        else:
            _obj = cls(serial_number=serial_number, **kwargs) # , cryptokey=cryptokey
        return _obj
    

    def __attrs_post_init__(self):
        self.init_EasyTimeSyncParsingMixin()
        

    async def initialize_connection(self):
        """
        Initialize connection based on connection_type.
        
        Creates the appropriate connection instance (BLE or USB) based on the
        connection_type field and establishes the connection.
        
        Supports three modes:
        - 'ble': Create BLEConnection instance
        - 'usb': Create USBHIDConnection instance  
        - 'auto': Try BLE first, fall back to USB on failure
        
        Raises:
            EmotivConnectionError: If connection fails for all attempted methods
        """
        from emotiv_lsl.connection_base import DeviceNotFoundError, EmotivConnectionError
        from emotiv_lsl.ble_connection import BLEConnection
        from emotiv_lsl.usb_connection import USBHIDConnection
        
        logger = logging.getLogger(f'emotiv.{self.device_name.replace(" ", "_").lower()}')
        
        if self.connection_type == 'ble':
            logger.info("Initializing BLE connection...")
            device_address = self.connection_config.get('device_address', None)
            self.connection = BLEConnection(device_address=device_address)
            await self.connection.connect()
            device_info = self.connection.get_device_info()
            logger.info(
                f"BLE connection established: {device_info['device_name']} "
                f"({device_info['device_id']})"
            )
            
        elif self.connection_type == 'usb':
            logger.info("Initializing USB HID connection...")
            self.connection = USBHIDConnection()
            await self.connection.connect()
            device_info = self.connection.get_device_info()
            logger.info(
                f"USB connection established: {device_info['device_name']} "
                f"({device_info['device_id']})"
            )
            
        elif self.connection_type == 'auto':
            logger.info("Auto-detecting connection type (trying BLE first, then USB)...")
            
            # Try BLE first
            try:
                device_address = self.connection_config.get('device_address', None)
                self.connection = BLEConnection(device_address=device_address)
                await self.connection.connect()
                device_info = self.connection.get_device_info()
                logger.info(
                    f"BLE connection established: {device_info['device_name']} "
                    f"({device_info['device_id']})"
                )
                return
            except (DeviceNotFoundError, Exception) as e:
                logger.info(f"BLE connection failed: {e}, trying USB...")
                self.connection = None
            
            # Fall back to USB
            try:
                self.connection = USBHIDConnection()
                await self.connection.connect()
                device_info = self.connection.get_device_info()
                logger.info(
                    f"USB connection established: {device_info['device_name']} "
                    f"({device_info['device_id']})"
                )
            except Exception as e:
                logger.error(f"USB connection also failed: {e}")
                raise EmotivConnectionError(
                    "Failed to connect via both BLE and USB. "
                    "Ensure device is powered on and accessible."
                )
        else:
            raise ValueError(
                f"Invalid connection_type: {self.connection_type}. "
                "Must be 'usb', 'ble', or 'auto'"
            )

    def get_crypto_key(self) -> bytearray:
        raise NotImplementedError('get_crypto_key method must be implemented in subclass')


    def get_lsl_source_id(self) -> str:
        return f"{self.device_name}_{self.KeyModel}_{self.get_crypto_key()}"


    def get_hid_device(self):
        # raise NotImplementedError(f'Specific hardware class (e.g. Epoc X) must override this to provide a concrete implementation.')
        import hid
        for device in hid.enumerate():
            if device.get('manufacturer_string', '') == 'Emotiv' and ((device.get('usage', 0) == 2 or device.get('usage', 0) == 0 and device.get('interface_number', 0) == 1)):
                return device
        raise Exception('Emotiv Epoc Base Headset not found')
        pass
    


    def add_lsl_outlet_info_common(self, info: StreamInfo) -> StreamInfo:
        """ adds common LSL metadata
        """
        # Add some metadata
        info.desc().append_child_value("manufacturer", "emotiv_lsl")
        info.desc().append_child_value("version", "0.1.1")
        info.desc().append_child_value("description", "Logged by the open-source tool 'emotiv_lsl' to record raw data from Emotiv headsets.")
        ## add a custom timestamp field to the stream info:
        info = self.EasyTimeSyncParsingMixin_add_lsl_outlet_info(info=info)
        return info
    


    def get_lsl_outlet_eeg_stream_info(self) -> StreamInfo:
        """Create LSL stream for EEG sensor data"""
        info = self.add_lsl_outlet_info_common(info=info)
        return info

    def get_lsl_outlet_motion_stream_info(self) -> StreamInfo:
        """Create LSL stream info for motion sensor data (accelerometer + gyroscope)"""
        info = self.add_lsl_outlet_info_common(info=info)
        return info
    

    def get_lsl_outlet_raw_debugging_stream_info(self) -> StreamInfo:
        """ 
        raw_packet_outlet = None
        if self.is_reverse_engineer_mode:
            raw_packet_outlet = StreamOutlet(self.get_lsl_outlet_raw_debugging_stream_info())
            print(f'Setup raw_packet_outlet (for reverse-engineering)')
            
        """
        packet_size = 32  # bytes
        dtype = 'int8'
        info = StreamInfo('Epoc X DebugRaw', type="Raw", channel_count=packet_size, nominal_srate=0, channel_format=dtype, source_id="debug_raw_001")
        info = self.add_lsl_outlet_info_common(info=info)
        return info
    

    def get_lsl_outlet_electrode_quality_stream_info(self) -> StreamInfo:
        """ Create LSL stream for EEG sensor quality data. Only active if `self.enable_electrode_quality_stream` is True """
        info = self.add_lsl_outlet_info_common(info=info)
        pass
    
        

    def decode_data(self) -> Tuple[List, Optional[List]]:
        raise NotImplementedError(f'Specific hardware class (e.g. Epoc X) must override this to provide a concrete implementation.')
        pass

    def validate_data(self, data) -> bool:
        raise NotImplementedError(f'Specific hardware class (e.g. Epoc X) must override this to provide a concrete implementation.')
        pass


    ## CyKit Conversion/Decoding/Data Packet Parsing Functions
    def convertEPOC_PLUS(self, value_1, value_2):
        edk_value = "%.8f" % (((int(value_1) * .128205128205129) + 4201.02564096001) + ((int(value_2) - 128) * 32.82051289))
        return edk_value
    
    # In the EEG class, add a method to extract quality values
    def extractQualityValues(self, data, return_as_array: bool=True) -> Union[NDArray, Dict[str, float]]:
        # Quality values are typically in specific bytes of the data packet
        # For EPOC/EPOC+, quality values are often in data[16] and data[17]
        quality_values_dict = {}

        # Different models store quality data differently
        if self.KeyModel == 2 or self.KeyModel == 1:  # Epoc
            # Extract quality values for each channel
            # This is a simplified example - actual implementation depends on the device's data format
            quality_values_dict = {'AF3': data[16] & 0xF, 'F7': (data[16] >> 4) & 0xF, 
                            'F3': data[17] & 0xF, 'FC5': (data[17] >> 4) & 0xF,
                            'T7': data[18] & 0xF, 'P7': (data[18] >> 4) & 0xF,
                            'O1': data[19] & 0xF, 'O2': (data[19] >> 4) & 0xF,
                            'P8': data[20] & 0xF, 'T8': (data[20] >> 4) & 0xF,
                            'FC6': data[21] & 0xF, 'F4': (data[21] >> 4) & 0xF,
                            'F8': data[22] & 0xF, 'AF4': (data[22] >> 4) & 0xF}
        elif (self.KeyModel == 6) or (self.KeyModel == 5) or (self.KeyModel == 8):  # Epoc+ or EpocX
            # Similar extraction for EPOC+
            quality_values_dict = {'AF3': data[16] & 0xF, 'F7': (data[16] >> 4) & 0xF, 
                            'F3': data[17] & 0xF, 'FC5': (data[17] >> 4) & 0xF,
                            'T7': data[18] & 0xF, 'P7': (data[18] >> 4) & 0xF,
                            'O1': data[19] & 0xF, 'O2': (data[19] >> 4) & 0xF,
                            'P8': data[20] & 0xF, 'T8': (data[20] >> 4) & 0xF,
                            'FC6': data[21] & 0xF, 'F4': (data[21] >> 4) & 0xF,
                            'F8': data[22] & 0xF, 'AF4': (data[22] >> 4) & 0xF}
        else:
            raise NotImplementedError(self.KeyModel)

        if return_as_array and (quality_values_dict is not None):
            return np.array([quality_values_dict[k] for k in self.eeg_channel_names]) ## ensures consistent channel order
        else:
            # returnt he dict
            return quality_values_dict
        


    async def main_loop_async(self):
        """
        Async version of main loop that uses connection abstraction.
        
        This method initializes the connection, creates LSL outlets, and continuously
        reads packets from the device (USB or BLE) and pushes them to LSL streams.
        Includes reconnection logic with retry attempts.
        """
        from emotiv_lsl.connection_base import EmotivConnectionError
        from emotiv_lsl.connection_status import ConnectionStatus
        from datetime import datetime
        
        logger = logging.getLogger(f'emotiv.{self.device_name.replace(" ", "_").lower()}')
        
        # Initialize connection
        await self.initialize_connection()
        
        # Initialize cipher after connection is established (for EmotivEpocX)
        if hasattr(self, 'initialize_cipher'):
            self.initialize_cipher()
        
        # Initialize connection status monitoring
        connection_status = ConnectionStatus()
        device_info = self.connection.get_device_info()
        connection_status.update_from_device_info(device_info)
        
        # Create EEG outlet
        eeg_outlet = None 

        # Create motion outlet if the device supports it
        motion_outlet = None
        if self.has_motion_data:
            motion_outlet = StreamOutlet(self.get_lsl_outlet_motion_stream_info())
            logger.info('Setup motion outlet')
            
        # Create raw packet outlet for reverse engineering
        raw_packet_outlet = None
        if self.is_reverse_engineer_mode:
            raw_packet_outlet = StreamOutlet(self.get_lsl_outlet_raw_debugging_stream_info())
            logger.info('Setup raw_packet_outlet (for reverse-engineering)')
            
        eeg_quality_outlet = None
        
        packet_count = 0
        reconnect_attempts = 0
        max_reconnect_attempts = 3
        reconnect_delay = 5  # seconds
        
        # Packet rate monitoring
        last_rate_check_time = datetime.now()
        rate_check_interval = 5.0  # seconds
        expected_eeg_rate = 128.0  # Hz
        rate_warning_threshold = 0.9  # 90% of expected rate
        
        while True:
            try:
                # Read packet from connection (USB or BLE)
                data = await self.connection.read_packet()
                
                if data is None:
                    # No packet available, continue
                    continue
                
                packet_count += 1
                packet_receive_time = datetime.now()
                
                # Debug logging for BLE packets
                if self.enable_debug_logging:
                    logger.debug(f"Packet #{packet_count}: Received {len(data)} bytes")
                    logger.debug(f"Raw packet hex: {data.hex()}")
                    
                    # Log BLE notification metadata if available
                    if hasattr(self.connection, '_last_sender') and self.connection._last_sender:
                        logger.debug(f"BLE notification from characteristic: {self.connection._last_sender}")
                
                if self.is_reverse_engineer_mode and raw_packet_outlet is not None:
                    # Output the raw data
                    raw_packet_outlet.push_sample(data)

                if self.validate_data(data):
                    if self.enable_debug_logging:
                        logger.debug(f"Packet #{packet_count}: Valid data packet, length={len(data)}")
                    
                    # Record successful packet for rate monitoring
                    connection_status.record_packet()

                    decoded, eeg_quality_data = self.decode_data(data)
                    
                    if (eeg_quality_data is not None) and len(eeg_quality_data) == 14:
                        if self.is_reverse_engineer_mode:
                            logger.debug(f'got eeg quality data: {eeg_quality_data}')
                        if eeg_quality_outlet is None:
                            eeg_quality_outlet = StreamOutlet(self.get_lsl_outlet_electrode_quality_stream_info())
                            logger.debug('set up EEG Sensor Quality outlet!')
                        eeg_quality_outlet.push_sample(eeg_quality_data)
                        
                    if decoded is not None:
                        # Check if this is motion data (based on number of channels)
                        if len(decoded) == 6:
                            if self.enable_debug_logging:
                                logger.debug(f"Packet #{packet_count}: Motion data decoded, {len(decoded)} channels")
                            if not self.has_motion_data:
                                self.has_motion_data = True
                                logger.debug('got first motion data!')

                            if motion_outlet is None:
                                motion_outlet = StreamOutlet(self.get_lsl_outlet_motion_stream_info())
                                logger.debug('set up motion outlet!')
                            motion_outlet.push_sample(decoded)
                            
                            # Measure latency for BLE connections
                            if self.enable_debug_logging and hasattr(self.connection, '_last_notification_time'):
                                if self.connection._last_notification_time:
                                    latency_ms = (datetime.now() - self.connection._last_notification_time).total_seconds() * 1000
                                    logger.debug(f"Latency (notification to LSL push): {latency_ms:.2f} ms")
                                    
                                    if latency_ms > 50:
                                        logger.warning(
                                            f"High latency detected: {latency_ms:.2f} ms "
                                            f"(threshold: 50 ms). Performance may be degraded."
                                        )

                        elif len(decoded) == 14:  # EEG data has 14 channels
                            if self.enable_debug_logging:
                                logger.debug(f"Packet #{packet_count}: EEG data decoded, {len(decoded)} channels")
                            if eeg_outlet is None:
                                eeg_outlet = StreamOutlet(self.get_lsl_outlet_eeg_stream_info())
                                logger.debug('set up EEG outlet!')                                                        
                            eeg_outlet.push_sample(decoded)
                            
                            # Measure latency for BLE connections
                            if self.enable_debug_logging and hasattr(self.connection, '_last_notification_time'):
                                if self.connection._last_notification_time:
                                    latency_ms = (datetime.now() - self.connection._last_notification_time).total_seconds() * 1000
                                    logger.debug(f"Latency (notification to LSL push): {latency_ms:.2f} ms")
                                    
                                    if latency_ms > 50:
                                        logger.warning(
                                            f"High latency detected: {latency_ms:.2f} ms "
                                            f"(threshold: 50 ms). Performance may be degraded."
                                        )
                        else:
                            logger.debug(f"Packet #{packet_count}: Unknown data type with {len(decoded)} channels")
                    else:
                        logger.debug(f"Packet #{packet_count}: self.decode_data(data) failed -- data packet (skipped)")
                else:
                    logger.debug(f"Packet #{packet_count}: Invalid data packet, length={len(data)}")
                    # Record invalid packet as error
                    connection_status.record_error()
                
                # Check packet rate periodically
                current_time = datetime.now()
                time_since_last_check = (current_time - last_rate_check_time).total_seconds()
                
                if time_since_last_check >= rate_check_interval:
                    # Calculate current packet rate
                    current_rate = connection_status.calculate_packet_rate(window_seconds=5.0)
                    
                    # Log warning if rate drops below threshold
                    if current_rate > 0 and current_rate < (expected_eeg_rate * rate_warning_threshold):
                        logger.warning(
                            f"Packet rate below expected: {current_rate:.1f} Hz "
                            f"(expected: {expected_eeg_rate:.1f} Hz, "
                            f"threshold: {expected_eeg_rate * rate_warning_threshold:.1f} Hz)"
                        )
                    elif current_rate > 0:
                        logger.debug(f"Packet rate: {current_rate:.1f} Hz")
                    
                    # Log error count if there are errors
                    if connection_status.error_count > 0:
                        logger.info(
                            f"Connection status - Rate: {current_rate:.1f} Hz, "
                            f"Errors: {connection_status.error_count}, "
                            f"Total packets: {packet_count}"
                        )
                    
                    last_rate_check_time = current_time
                    
            except (EmotivConnectionError, ConnectionError, Exception) as e:
                logger.error(f"Connection error after {packet_count} packets: {e}")
                reconnect_attempts += 1
                
                if reconnect_attempts >= max_reconnect_attempts:
                    logger.error(
                        f"Max reconnection attempts ({max_reconnect_attempts}) reached. "
                        "Terminating gracefully."
                    )
                    break
                
                logger.info(
                    f"Attempting reconnection {reconnect_attempts}/{max_reconnect_attempts} "
                    f"in {reconnect_delay} seconds..."
                )
                await asyncio.sleep(reconnect_delay)
                
                try:
                    # Disconnect and reconnect
                    if self.connection:
                        await self.connection.disconnect()
                    await self.initialize_connection()
                    logger.info("Reconnection successful")
                    reconnect_attempts = 0  # Reset counter on successful reconnection
                except Exception as reconnect_error:
                    logger.error(f"Reconnection attempt failed: {reconnect_error}")
        
        # Clean up connection on exit
        if self.connection:
            await self.connection.disconnect()
            logger.info("Connection closed")

    def main_loop(self):
        """
        Synchronous wrapper for main_loop_async.
        
        This method maintains backward compatibility with existing code that
        calls main_loop() synchronously. It runs the async main_loop_async()
        using asyncio.run().
        """
        asyncio.run(self.main_loop_async())