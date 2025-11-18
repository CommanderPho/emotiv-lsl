"""
BLE UUID Discovery Utility for Emotiv Headsets

This script scans for Emotiv EPOC X headsets via Bluetooth Low Energy,
connects to discovered devices, and enumerates all GATT services and
characteristics. The discovered UUIDs are saved to a JSON configuration
file for use in the BLE connection implementation.

Usage:
    python scripts/discover_ble_uuids.py
    python scripts/discover_ble_uuids.py --address AA:BB:CC:DD:EE:FF
    python scripts/discover_ble_uuids.py --timeout 60
"""

import asyncio
import argparse
import json
import logging
from pathlib import Path
from typing import Optional, Dict, List
from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def discover_emotiv_devices(timeout: float = 30.0) -> List[BLEDevice]:
    """
    Scan for Emotiv headsets via BLE.
    
    Args:
        timeout: Discovery timeout in seconds
        
    Returns:
        List of discovered Emotiv BLE devices
    """
    logger.info(f"Scanning for Emotiv devices (timeout: {timeout}s)...")
    
    devices = await BleakScanner.discover(timeout=timeout)
    
    # Filter for Emotiv devices
    emotiv_devices = [
        device for device in devices
        if device.name and 'EPOC' in device.name.upper()
    ]
    
    if emotiv_devices:
        logger.info(f"Found {len(emotiv_devices)} Emotiv device(s):")
        for device in emotiv_devices:
            logger.info(f"  - {device.name} ({device.address}) RSSI: {device.rssi} dBm")
    else:
        logger.warning("No Emotiv devices found")
    
    return emotiv_devices


async def enumerate_gatt_services(device_address: str) -> Dict:
    """
    Connect to a BLE device and enumerate all GATT services and characteristics.
    
    Args:
        device_address: MAC address of the BLE device
        
    Returns:
        Dictionary containing device info and GATT structure
    """
    logger.info(f"Connecting to device: {device_address}")
    
    device_info = {
        "device_address": device_address,
        "services": []
    }
    
    async with BleakClient(device_address, timeout=10.0) as client:
        logger.info(f"Connected: {client.is_connected}")
        
        # Get device name if available
        try:
            device_name = await client.read_gatt_char("00002a00-0000-1000-8000-00805f9b34fb")
            device_info["device_name"] = device_name.decode('utf-8')
            logger.info(f"Device name: {device_info['device_name']}")
        except Exception:
            device_info["device_name"] = "Unknown"
        
        # Enumerate all services
        logger.info("\nEnumerating GATT services and characteristics:")
        logger.info("=" * 80)
        
        for service in client.services:
            service_data = {
                "uuid": service.uuid,
                "description": service.description,
                "characteristics": []
            }
            
            logger.info(f"\nService: {service.uuid}")
            logger.info(f"  Description: {service.description}")
            
            # Enumerate characteristics for this service
            for char in service.characteristics:
                char_data = {
                    "uuid": char.uuid,
                    "description": char.description,
                    "properties": char.properties
                }
                
                logger.info(f"  Characteristic: {char.uuid}")
                logger.info(f"    Description: {char.description}")
                logger.info(f"    Properties: {', '.join(char.properties)}")
                
                # Try to read characteristic if readable
                if "read" in char.properties:
                    try:
                        value = await client.read_gatt_char(char.uuid)
                        char_data["sample_value"] = value.hex()
                        logger.info(f"    Sample value: {value.hex()}")
                    except Exception as e:
                        logger.debug(f"    Could not read: {e}")
                
                # List descriptors
                if char.descriptors:
                    char_data["descriptors"] = []
                    logger.info(f"    Descriptors:")
                    for desc in char.descriptors:
                        desc_data = {
                            "uuid": desc.uuid,
                            "description": desc.description
                        }
                        char_data["descriptors"].append(desc_data)
                        logger.info(f"      - {desc.uuid}: {desc.description}")
                
                service_data["characteristics"].append(char_data)
            
            device_info["services"].append(service_data)
        
        logger.info("=" * 80)
    
    return device_info


def save_uuids_to_file(device_info: Dict, output_path: Path) -> None:
    """
    Save discovered UUIDs to a JSON configuration file.
    
    Args:
        device_info: Dictionary containing device and GATT information
        output_path: Path to output JSON file
    """
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write JSON file with pretty formatting
    with open(output_path, 'w') as f:
        json.dump(device_info, f, indent=2)
    
    logger.info(f"\nUUIDs saved to: {output_path}")


async def main(device_address: Optional[str] = None, discovery_timeout: float = 30.0):
    """
    Main discovery workflow.
    
    Args:
        device_address: Optional MAC address to connect to specific device
        discovery_timeout: Timeout for device discovery in seconds
    """
    try:
        # If no address specified, discover devices
        if not device_address:
            devices = await discover_emotiv_devices(timeout=discovery_timeout)
            
            if not devices:
                logger.error("No Emotiv devices found. Please ensure:")
                logger.error("  1. The headset is powered on")
                logger.error("  2. Bluetooth is enabled on your computer")
                logger.error("  3. The headset is not connected to another device")
                return
            
            # Use the first discovered device
            device_address = devices[0].address
            logger.info(f"\nUsing device: {devices[0].name} ({device_address})")
        
        # Enumerate GATT services and characteristics
        device_info = await enumerate_gatt_services(device_address)
        
        # Save to configuration file
        output_path = Path(__file__).parent.parent / "emotiv_lsl" / "ble_uuids.json"
        save_uuids_to_file(device_info, output_path)
        
        # Print summary
        logger.info("\n" + "=" * 80)
        logger.info("DISCOVERY SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Device: {device_info.get('device_name', 'Unknown')} ({device_info['device_address']})")
        logger.info(f"Services found: {len(device_info['services'])}")
        
        total_chars = sum(len(svc['characteristics']) for svc in device_info['services'])
        logger.info(f"Characteristics found: {total_chars}")
        
        # Identify potential data characteristics
        logger.info("\nCharacteristics with NOTIFY property (potential data streams):")
        for service in device_info['services']:
            for char in service['characteristics']:
                if 'notify' in char['properties']:
                    logger.info(f"  - {char['uuid']} ({char['description']})")
        
        logger.info("\nNext steps:")
        logger.info("  1. Review the generated ble_uuids.json file")
        logger.info("  2. Identify the characteristics for EEG and motion data")
        logger.info("  3. Update BLEConnection class with the correct UUIDs")
        
    except Exception as e:
        logger.error(f"Error during discovery: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Discover BLE GATT services and characteristics for Emotiv headsets"
    )
    parser.add_argument(
        "--address",
        "-a",
        type=str,
        help="MAC address of specific device to connect to (e.g., AA:BB:CC:DD:EE:FF)"
    )
    parser.add_argument(
        "--timeout",
        "-t",
        type=float,
        default=30.0,
        help="Discovery timeout in seconds (default: 30)"
    )
    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run the async main function
    asyncio.run(main(device_address=args.address, discovery_timeout=args.timeout))
