#!/bin/bash

# Exit on any error
set -e

# Define variables
MINICONDA_VERSION="latest"
MINICONDA_INSTALLER="Miniconda3-${MINICONDA_VERSION}-Linux-x86_64.sh"
MINICONDA_URL="https://repo.anaconda.com/miniconda/${MINICONDA_INSTALLER}"
INSTALL_DIR="$(pwd)/miniconda3"  # Install in current directory

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if conda is already installed in current directory
if [ -d "$INSTALL_DIR" ]; then
    echo "Conda is already installed in current directory, updating installation..."
    export PATH="$INSTALL_DIR/bin:$PATH"
    conda update -n base -c defaults conda -y -q
else
    echo "Installing Conda in current directory..."
    # Create a temporary directory for downloads
    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR"

    echo "Downloading Miniconda installer..."
    wget -q "$MINICONDA_URL" -O "$MINICONDA_INSTALLER"

    echo "Installing Miniconda..."
    bash "$MINICONDA_INSTALLER" -b -p "$INSTALL_DIR"

    # Add conda to path for current session
    export PATH="$INSTALL_DIR/bin:$PATH"

    # Cleanup installer
    cd - > /dev/null
    rm -rf "$TEMP_DIR"
fi

# Initialize conda for current shell
eval "$("$INSTALL_DIR/bin/conda" 'shell.bash' 'hook')"

# Configure conda settings
conda config --set auto_activate_base false
conda config --set channel_priority flexible
conda config --add channels conda-forge

echo "Installing OpenMM and dependencies..."
# Install OpenMM from conda-forge with specific version
conda install -c conda-forge python=3.10 openmm=8.0.0 pdbfixer=1.9 -y -q

echo "Installing Python dependencies..."
python3 -m pip install --no-cache-dir -r requirements.txt

echo "Installing TensorFlow with CUDA support..."
python3 -m pip install --no-cache-dir 'tensorflow[and-cuda]'

echo "Verifying TensorFlow GPU installation..."
python -c "
import tensorflow as tf
gpus = tf.config.list_physical_devices('GPU')
print('TensorFlow GPU(s):', gpus)
"

echo "Installation complete!"
