import asyncio
import threading
import queue
import time
import logging

from bleak import BleakClient, BleakScanner
from emotiv_lsl.helpers import HardwareConnectionBackend, CyKitCompatibilityHelpers

DEVICE_UUID = "{81072f40-9f3d-11e3-a9dc-0002a5d5c51b}".lower()
DATA_UUID   = "{81072f41-9f3d-11e3-a9dc-0002a5d5c51b}".lower()
MEMS_UUID   = "{81072f42-9f3d-11e3-a9dc-0002a5d5c51b}".lower()

logger = logging.getLogger(__name__)


class BleHidLikeDevice:
    """Minimal HID-like wrapper over Bleak notifications.

    Exposes read(size) that blocks until `size` bytes are available.
    """

    def __init__(self, device_name_hint: str = "EPOC", connect_timeout_s: float = 45.0, scan_interval_s: float = 3.0, attempt_notify: bool = True):
        self._device_name_hint = device_name_hint
        self._device_info_dict = None
        self._client = None
        self._loop = None
        self._thread = None
        self._in_q = queue.Queue()
        self._buffer = bytearray()
        self._connected_event = threading.Event()
        self._stop_event = threading.Event()
        self._connect_timeout_s = max(1.0, float(connect_timeout_s))
        self._scan_interval_s = max(0.5, float(scan_interval_s))
        self._attempt_notify = bool(attempt_notify)

        # Start background BLE thread
        self._thread = threading.Thread(target=self._run_loop, name="BleHidLoop", daemon=True)
        self._thread.start()

        # Wait for connection or immediate init error (with timeout)
        deadline = time.time() + self._connect_timeout_s
        while not self._connected_event.is_set():
            remaining = deadline - time.time()
            if remaining <= 0:
                break
            try:
                # Poll for exceptions from the BLE thread to surface immediately
                item = self._in_q.get(timeout=min(0.25, max(0.0, remaining)))
                if isinstance(item, Exception):
                    raise item
                else:
                    # Data before connected shouldn't happen, ignore
                    pass
            except queue.Empty:
                # No exception yet; loop again until connected or timeout
                pass
        if not self._connected_event.is_set():
            raise TimeoutError("BLE connect timeout")
        else:
            logger.info(f"BleHidLikeDevice._init(): FULLY READY!")


    @property
    def serial_number(self):
        """The serial_number property."""
        if self._device_info_dict is None:
            return None
        return (self._device_info_dict or {}).get('headset_serial_number', None)
        # return bytes(("\x00" * 12),'utf-8') + bytearray.fromhex(str(BT_key[6:8] + BT_key[4:6] + BT_key[2:4] + BT_key[0:2]))
    @serial_number.setter
    def serial_number(self, value):
        if self._device_info_dict is None:
            self._device_info_dict = {}
        self._device_info_dict['headset_serial_number'] = value


    def _run_loop(self):
        try:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            self._loop.run_until_complete(self._async_init())
            # Keep loop alive until stop requested
            while not self._stop_event.is_set():
                self._loop.run_until_complete(asyncio.sleep(0.1))
        except Exception as exc:
            # Surface errors by putting an exception sentinel into the queue
            self._in_q.put(exc)
        finally:
            if self._client and self._client.is_connected:
                try:
                    self._loop.run_until_complete(self._client.disconnect())
                except Exception:
                    pass
            try:
                self._loop.stop()
            except Exception:
                pass

    async def _async_init(self):
        # Repeatedly scan until device found or timeout
        start_time = time.time()
        found_dev = None
        while (found_dev is None) and ((time.time() - start_time) < self._connect_timeout_s) and (not self._stop_event.is_set()):
            try:
                devices = await BleakScanner.discover()
            except Exception as scan_exc:
                logger.warning(f"BLE scan failed: {scan_exc}")
                devices = []

            for dev in devices:
                if dev is None:
                    continue
                name_value = (dev.name or "")
                if name_value and (self._device_name_hint.lower() in name_value.lower()):
                    # Build and store info about the discovered device, mirroring the example structure
                    info_dict = {'address': dev.address, 'name': dev.name, 'details': dev.details}
                    a_name = dev.name or ""
                    if a_name.startswith('EPOC'):
                        try:
                            *headset_name_parts, headset_BT_hex_key = a_name.split(' ')
                            headset_name = ' '.join(headset_name_parts)
                            headset_BT_hex_key = headset_BT_hex_key.strip(')(')
                            info_dict['headset_name'] = headset_name
                            info_dict['headset_BT_hex_key'] = headset_BT_hex_key
                            if len(headset_BT_hex_key) == 8:
                                serial_number = bytes(("\x00" * 12),'utf-8') + bytearray.fromhex(str(headset_BT_hex_key[6:8] + headset_BT_hex_key[4:6] + headset_BT_hex_key[2:4] + headset_BT_hex_key[0:2]))
                                info_dict['headset_serial_number'] = serial_number
                        except Exception:
                            # Non-fatal; still proceed with device
                            pass
                    self._device_info_dict = info_dict
                    logger.info(f"found device: {info_dict}")
                    found_dev = dev
                    break

            if found_dev is None:
                # Wait a bit before rescanning
                await asyncio.sleep(self._scan_interval_s)
        ## END while (found_dev is None) and ((time....
        logger.info(f"done enumerating devices found_dev: {found_dev}\tinfo_dict: {self._device_info_dict}")

        if found_dev is None:
            raise RuntimeError(f"BLE device not found matching hint '{self._device_name_hint}' within {self._connect_timeout_s}s")

        # Connect
        self._client = BleakClient(found_dev)
        logger.info(f"found_device, connecting...")
        await self._client.connect()
        if self._client.is_connected:
            logger.info(f"Connected to {found_dev}\tinfo_dict: {self._device_info_dict}")
        else:
            raise RuntimeError(f"Could not connect to {found_dev}")

        # Signal connected immediately so constructor can proceed
        self._connected_event.set()

        # Optionally send start streaming command here if needed
        # await self._client.write_gatt_char(DATA_UUID, b"\x01\x00", response=False)

        if self._attempt_notify:
            await self._client.start_notify(DATA_UUID, self._on_notification)
            # MEMS is optional; ignore errors
            try:
                await self._client.start_notify(MEMS_UUID, self._on_notification)
            except Exception:
                pass

    def _on_notification(self, _handle, data: bytearray):
        # Push raw bytes into queue
        self._in_q.put(bytes(data))


    def read(self, size: int, timeout_ms: int = 0):
        """Block until `size` bytes are available, then return exactly that many.

        Mimics hid.Device.read which returns a bytes-like object of length <= size.
        Here we aggregate from notifications until we have `size` bytes.
        """
        deadline = time.time() + (timeout_ms / 1000.0 if timeout_ms and timeout_ms > 0 else 0)

        # Drain queue into buffer until enough collected
        while len(self._buffer) < size:
            remaining = None
            if timeout_ms and timeout_ms > 0:
                remaining = max(0, deadline - time.time())
                if remaining == 0:
                    break
            try:
                chunk = self._in_q.get(timeout=remaining)
                if isinstance(chunk, Exception):
                    raise chunk
                self._buffer.extend(chunk)
            except queue.Empty:
                break

        if len(self._buffer) == 0:
            return []

        # Return exactly `size` (or whatever is available if smaller)
        out = self._buffer[:size]
        del self._buffer[:len(out)]
        # hid.Device.read returns a list of ints; maintain compatibility with caller expecting iterable of ints
        return list(out)

    def close(self):
        self._stop_event.set()
        if self._loop is not None:
            try:
                # Schedule disconnect and stop
                async def _shutdown():
                    try:
                        if self._client and self._client.is_connected:
                            await self._client.stop_notify(DATA_UUID)
                            try:
                                await self._client.stop_notify(MEMS_UUID)
                            except Exception:
                                pass
                            await self._client.disconnect()
                    except Exception:
                        pass
                asyncio.run_coroutine_threadsafe(_shutdown(), self._loop).result(timeout=5)
            except Exception:
                pass
        if self._thread is not None and self._thread.is_alive():
            try:
                self._thread.join(timeout=2)
            except Exception:
                pass

    @classmethod
    async def discover_devices(cls):
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
                
        logger.info(f"done.")
        # print(f'devices: {devices}')
        # return devices
    



if __name__ == "__main__":
    # Configure logging for debugging data packets
    logging.basicConfig(
        # level=logging.DEBUG,
        level=logging.WARNING,
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

    # found_devices = BleHidLikeDevice.discover_devices()
    # print(f'found_devices: {found_devices}')
    # 949F7EA5-0829-05F7-3441-7BAABB0F0064: EPOCX (E50202E9)
    
    asyncio.run(BleHidLikeDevice.discover_devices())

    # hw_device = BleHidLikeDevice()
    # hw_device
    
    # hw_device._device_name_hint
    
    # hw_device.close()
    # crypto_key = emotiv_epoc_x.get_crypto_key()
    # print(f'crypto_key: {crypto_key}')
    # emotiv_epoc_x.main_loop()

