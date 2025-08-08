#!/bin/bash

# Keyword to identify the Emotiv dongle in device descriptions
EMOTIV_KEYWORD="Emotiv"

echo "Searching for Emotiv dongle..."

# Detect operating system
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "Detected macOS system"
    
    # Use system_profiler to find USB devices on macOS
    # Suppress system_profiler warnings by redirecting stderr
    DEVICE_INFO=$(system_profiler SPUSBDataType 2>/dev/null | grep -A 5 -B 5 "$EMOTIV_KEYWORD" | head -20)
    
    if [ -z "$DEVICE_INFO" ]; then
        echo "Error: Emotiv dongle not found. Please verify it is properly connected."
        exit 1
    fi
    
    echo "Emotiv device detected:"
    echo "$DEVICE_INFO"
    
    # Extract USB ID from system_profiler output
    USB_ID=$(system_profiler SPUSBDataType 2>/dev/null | grep -A 10 "$EMOTIV_KEYWORD" | grep "Product ID" | head -1 | sed 's/.*Product ID: 0x//')
    
    if [ -z "$USB_ID" ]; then
        echo "Error: Could not extract USB ID from device information."
        exit 1
    fi
    
    # Convert hex to decimal for consistency
    USB_ID_DECIMAL=$(printf "%d" "0x$USB_ID")
    USB_ID=$USB_ID_DECIMAL
    
    echo "USB ID detected: $USB_ID"
    
    # On macOS, Docker has limited USB device access
    # We'll use a different approach for macOS
    DEVICE_PATH="/dev/null"
    
else
    # Linux
    echo "Detected Linux system"
    
    # Find the line containing the Emotiv dongle
    DEVICE_INFO=$(lsusb | grep "$EMOTIV_KEYWORD")
    
    if [ -z "$DEVICE_INFO" ]; then
        echo "Error: Emotiv dongle not found. Please verify it is properly connected."
        exit 1
    fi
    
    echo "Emotiv device detected: $DEVICE_INFO"
    
    # Extract Bus, Device and ID
    BUS=$(echo "$DEVICE_INFO" | awk '{print $2}')
    DEVICE=$(echo "$DEVICE_INFO" | awk '{print $4}' | sed 's/://')
    USB_ID=$(echo "$DEVICE_INFO" | awk '{print $6}')
    
    # Build the complete path
    DEVICE_PATH="/dev/bus/usb/$BUS/$DEVICE"
    
    # Verify the device exists
    if [ ! -e "$DEVICE_PATH" ]; then
        echo "Error: Device path ($DEVICE_PATH) does not exist."
        exit 1
    fi
    
    echo "USB path detected: $DEVICE_PATH"
    echo "USB ID detected: $USB_ID"
fi

# Generate or update docker-compose.yml
DOCKER_COMPOSE_FILE="docker-compose.yml"

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS configuration - limited USB device access
    cat > $DOCKER_COMPOSE_FILE <<EOF
version: '3.8'

services:
  python-app:
    build: .
    container_name: python_pylsl_emotiv
    privileged: true
    volumes:
      - .:/app
    environment:
      - PYTHONUNBUFFERED=1
      - USB_DEVICE=$USB_ID
      - PLATFORM=macos
    command: ["conda", "run", "-n", "lsl_env", "python", "main.py"]
EOF
else
    # Linux configuration - full USB device access
    cat > $DOCKER_COMPOSE_FILE <<EOF
version: '3.8'

services:
  python-app:
    devices:
      - /dev/hidraw0:/dev/hidraw0
      - /dev/hidraw1:/dev/hidraw1
      - ${DEVICE_PATH}:${DEVICE_PATH}
    build: .
    container_name: python_pylsl_emotiv
    privileged: true
    volumes:
      - .:/app
    environment:
      - PYTHONUNBUFFERED=1
      - USB_DEVICE=$USB_ID
      - PLATFORM=linux
    command: ["conda", "run", "-n", "lsl_env", "python", "main.py"]
EOF
fi

echo "File $DOCKER_COMPOSE_FILE updated successfully!"
echo "The Emotiv dongle is configured for Docker."

if [[ "$OSTYPE" == "darwin"* ]]; then
    echo ""
    echo "Note: On macOS, Docker has limited access to USB devices."
    echo "The application may need to be run outside of Docker for full USB access."
    echo "Consider running the application directly on macOS if USB access is required."
fi

# Launch Docker Compose with the detected device
echo "Launching Docker Compose..."
docker-compose up --build
