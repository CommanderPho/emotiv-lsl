import asyncio
import threading
import queue
import time
from bleak import BleakClient, BleakScanner

DEVICE_UUID = "{81072f40-9f3d-11e3-a9dc-0002a5d5c51b}".lower()
DATA_UUID   = "{81072f41-9f3d-11e3-a9dc-0002a5d5c51b}".lower()
MEMS_UUID   = "{81072f42-9f3d-11e3-a9dc-0002a5d5c51b}".lower()


class BleHidLikeDevice:
    """Minimal HID-like wrapper over Bleak notifications.

    Exposes read(size) that blocks until `size` bytes are available.
    """

    def __init__(self, device_name_hint: str = "EPOC+"):
        self._device_name_hint = device_name_hint
        self._client = None
        self._loop = None
        self._thread = None
        self._in_q = queue.Queue()
        self._buffer = bytearray()
        self._connected_event = threading.Event()
        self._stop_event = threading.Event()

        # Start background BLE thread
        self._thread = threading.Thread(target=self._run_loop, name="BleHidLoop", daemon=True)
        self._thread.start()

        # Wait for connection (with timeout)
        if not self._connected_event.wait(timeout=15.0):
            raise TimeoutError("BLE connect timeout")

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
        # Discover by name hint
        devices = await BleakScanner.discover()
        dev = next((d for d in devices if self._device_name_hint.lower() in (d.name or "").lower()), None)
        if dev is None:
            raise RuntimeError(f"BLE device with name containing '{self._device_name_hint}' not found")

        self._client = BleakClient(dev)
        await self._client.connect()

        # Optionally send start streaming command here if needed
        # await self._client.write_gatt_char(DATA_UUID, b"\x01\x00", response=False)

        await self._client.start_notify(DATA_UUID, self._on_notification)
        # MEMS is optional; uncomment if needed by caller to interleave streams
        try:
            await self._client.start_notify(MEMS_UUID, self._on_notification)
        except Exception:
            pass

        self._connected_event.set()

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

