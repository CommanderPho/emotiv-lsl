import logging
import os
import sys
import platform
import argparse

# Add the directory containing the HIDAPI DLL on Windows only
if sys.platform == "win32":
    arch_dir = "x64" if platform.architecture()[0] == "64bit" else "x86"
    project_root = os.path.dirname(os.path.abspath(__file__))
    dll_dir = os.path.join(project_root, "hidapi-win", arch_dir)
    if os.path.isdir(dll_dir):
        os.add_dll_directory(dll_dir)

# Hint the loader about bundled hidapi on macOS when frozen
if sys.platform == "darwin" and getattr(sys, 'frozen', False):
    exe_dir = os.path.dirname(sys.executable)
    # Prefer Frameworks inside the .app bundle
    frameworks_dir = os.path.normpath(os.path.join(exe_dir, '..', 'Frameworks'))
    candidates = [
        frameworks_dir,
        exe_dir,
    ]
    for candidate in candidates:
        if os.path.isdir(candidate):
            current = os.environ.get('DYLD_FALLBACK_LIBRARY_PATH', '')
            paths = [candidate] + ([current] if current else [])
            os.environ['DYLD_FALLBACK_LIBRARY_PATH'] = ':'.join(paths)
            break

from emotiv_lsl.emotiv_epoc_x import EmotivEpocX

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Emotiv LSL Server - Stream EEG data from Emotiv EPOC X headset',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                           # Auto-detect connection (BLE first, then USB)
  python main.py --connection usb          # Force USB HID connection
  python main.py --connection ble          # Force BLE connection
  python main.py --connection ble --ble-address AA:BB:CC:DD:EE:FF  # Connect to specific device
        """
    )
    
    parser.add_argument(
        '--connection',
        type=str,
        choices=['usb', 'ble', 'auto'],
        default='auto',
        help='Connection type: usb (USB HID dongle), ble (Bluetooth LE), or auto (try BLE first, fallback to USB). Default: auto'
    )
    
    parser.add_argument(
        '--ble-address',
        type=str,
        default=None,
        help='MAC address of specific BLE device to connect to (e.g., AA:BB:CC:DD:EE:FF). Only used with --connection ble'
    )
    
    args = parser.parse_args()
    
    # Configure logging for debugging data packets
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger("emotiv_lsl")
    
    # Display startup information
    logger.info("=" * 60)
    logger.info("Emotiv LSL Server Starting")
    logger.info("=" * 60)
    logger.info(f"Connection mode: {args.connection}")
    if args.connection == 'ble' and args.ble_address:
        logger.info(f"Target BLE device: {args.ble_address}")
    elif args.connection == 'auto':
        logger.info("Will attempt BLE connection first, then fallback to USB if unavailable")
    logger.info("=" * 60)
    
    # Prepare connection configuration
    connection_config = {}
    if args.ble_address:
        connection_config['device_address'] = args.ble_address
    
    # Create EmotivEpocX instance with connection parameters
    emotiv_epoc_x = EmotivEpocX(
        connection_type=args.connection,
        connection_config=connection_config
    )
    
    # Note: Crypto key initialization is deferred until after connection is established
    # It will be logged during the connection initialization in main_loop()
    
    # Start the main loop (this will initialize connection and cipher)
    emotiv_epoc_x.main_loop()
