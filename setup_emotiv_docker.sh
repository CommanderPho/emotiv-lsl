#!/bin/bash

# Keyword to identify the Emotiv dongle in device descriptions
EMOTIV_KEYWORD="Emotiv"

echo "Searching for Emotiv dongle..."

# Detect operating system
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "Detected macOS system"
    
    # Use system_profiler to find USB devices on macOS
    DEVICE_INFO=$(system_profiler SPUSBDataType | grep -A 5 -B 5 "$EMOTIV_KEYWORD" | head -20)
    
    if [ -z "$DEVICE_INFO" ]; then
        echo "Error: Emotiv dongle not found. Please verify it is properly connected."
        exit 1
    fi
    
    echo "Emotiv device detected:"
    echo "$DEVICE_INFO"
    
    # Extract USB ID from system_profiler output
    USB_ID=$(system_profiler SPUSBDataType | grep -A 10 "$EMOTIV_KEYWORD" | grep "Product ID" | head -1 | awk '{print $3}')
    
    if [ -z "$USB_ID" ]; then
        echo "Error: Could not extract USB ID from device information."
        exit 1
    fi
    
    echo "USB ID detected: $USB_ID"
    
    # On macOS, we'll use the USB ID for device mapping
    DEVICE_PATH="/dev/usb/$USB_ID"
    
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
    command: ["conda", "run", "-n", "lsl_env", "python", "main.py"]
EOF

echo "File $DOCKER_COMPOSE_FILE updated successfully!"
echo "The Emotiv dongle is configured for Docker."

# Launch Docker Compose with the detected device
echo "Launching Docker Compose..."
docker-compose up --build
