#!/bin/bash

set -e  # Exit on any error

# Function to log messages
log() {
    echo "📝 $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Get the absolute path of the repository
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Install system dependencies
log "Installing system dependencies..."
sudo apt update
sudo apt install -y pipx

# Ask about ffmpeg installation
read -p "Do you want to install ffmpeg and related libraries? [y/n]: " FFMPEG_CHOICE
if [ "$FFMPEG_CHOICE" = "y" ]; then
    log "Installing ffmpeg and related libraries..."
    sudo apt install -y ffmpeg libsdl2-mixer-2.0-0 libsdl2-2.0-0 libsdl2-mixer-dev python3-sdl2
else
    log "Skipping ffmpeg and related libraries installation..."
fi

pipx ensurepath

# Install poetry using pipx
if ! command_exists poetry; then
    log "Installing poetry..."
    pipx install poetry
    # Add poetry to PATH for this session
    export PATH="$HOME/.local/bin:$PATH"
fi

# Install python dependencies using poetry
log "Installing Python dependencies..."
poetry install

# Create media directory if it doesn't exist
mkdir -p "$REPO_DIR/media"

# Get syncUrl and password from user
read -p "Enter your AccessKit syncUrl: " SYNC_URL
read -p "Enter your AccessKit password: " PASSWORD

# Create config.json
log "Creating config.json..."
cat > "$REPO_DIR/config.json" << EOF
{
    "syncUrl": "$SYNC_URL",
    "password": "$PASSWORD"
}
EOF

# Ask about media file
read -p "Do you want to download a media file now? [y/n]: " DOWNLOAD_CHOICE
if [ "$DOWNLOAD_CHOICE" = "y" ]; then
    read -p "Enter media file URL: " MEDIA_URL
    log "Downloading media file..."
    wget -P "$REPO_DIR/media" "$MEDIA_URL"
else
    log "Skipping media file download. Please place your media file in $REPO_DIR/media when you have it."
fi

# Ask about autostart setup
log "Would you like to setup automatically starting the application when the device powers on (this will create a systemd service)? [y/n]"
read -p "> " START_CHOICE

if [ "$START_CHOICE" = "y" ]; then
    # systemd service setup
    SERVICE_NAME="ak-rpi.service"
    SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME"

    # Create service file
    sudo tee "$SERVICE_FILE" > /dev/null << EOF
[Unit]
Description=AK-RPI Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$REPO_DIR
ExecStart=$HOME/.local/bin/poetry run ak-rpi
Restart=always

[Install]
WantedBy=multi-user.target
EOF

    # Enable and start service
    sudo systemctl daemon-reload
    sudo systemctl enable "$SERVICE_NAME"
    sudo systemctl start "$SERVICE_NAME"
    log "Created and started systemd service $SERVICE_NAME"
else
    log "Skipping autostart setup. You'll need to start the service manually using 'poetry run ak-rpi'"
fi

log "Setup complete! Would you like to test the system now? (y/n)"
read -p "> " TEST_CHOICE

if [ "$TEST_CHOICE" = "y" ]; then
    poetry run ak-rpi
fi
