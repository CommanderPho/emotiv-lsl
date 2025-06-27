# Utiliser l'image Miniconda comme base
FROM continuumio/miniconda

# Créer et activer l'environnement conda
RUN conda create -y --name lsl_env python=3.8
SHELL ["conda", "run", "-n", "lsl_env", "/bin/bash", "-c"]

# Update Debian sources and install necessary dependencies
RUN sed -i 's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' /etc/apt/sources.list && \
    sed -i '/security.debian.org/d' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y libhidapi-dev libhidapi-hidraw0 libhidapi-libusb0 libusb-1.0-0-dev build-essential usbutils wireshark-common tshark tcpdump udev&& \
    apt-get clean
    
# Install liblsl (Lab Streaming Layer library)
RUN conda install -y -c conda-forge liblsl

# Configure shared library symbolic links
RUN ldconfig

# Copy project files to the image
COPY . /app

# Set working directory
WORKDIR /app

# Update pip and install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt --no-cache-dir && \
    pip install mne matplotlib

# Add PYTHONPATH to include local files
ENV PYTHONPATH="/app:$PYTHONPATH"

# Default entry point
CMD ["conda", "run", "-n", "lsl_env", "python", "main.py"]
