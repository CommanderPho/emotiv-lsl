import asyncio
from bleak import BleakClient, BleakScanner

DEVICE_UUID = "{81072f40-9f3d-11e3-a9dc-0002a5d5c51b}".lower()
DATA_UUID   = "{81072f41-9f3d-11e3-a9dc-0002a5d5c51b}".lower()
MEMS_UUID   = "{81072f42-9f3d-11e3-a9dc-0002a5d5c51b}".lower()

def on_data(_, data: bytearray):
    # mirror DataCallback logic here
    print("EEG:", data)

def on_mems(_, data: bytearray):
    print("MEMS:", data)

async def run():
    # Discover by name or by service UUID (if advertised)
    devices = await BleakScanner.discover()
    dev = next((d for d in devices if "EPOC+" in (d.name or "")), None)
    if not dev:
        raise RuntimeError("EPOC+ not found")

    async with BleakClient(dev) as client:
        # Optionally write control/start payload if your device requires it
        # await client.write_gatt_char(DATA_UUID, b"\x01\x00", response=False)

        await client.start_notify(DATA_UUID, on_data)
        await client.start_notify(MEMS_UUID, on_mems)
        await asyncio.sleep(999999)  # keep running

asyncio.run(run())

