#!/bin/bash

set -e  # Exit on any error

# Function to log messages
log() {
    echo " $1"
}

# Function to write ALSA config
write_alsa_config() {
    local config_file=$1
    local card_num=$2
    local device_num=$3

    # Backup existing config if it exists
    if [[ -f "$config_file" ]]; then
        cp "$config_file" "${config_file}.bak"
        log "Backed up existing $config_file to ${config_file}.bak"
    fi

    # Create parent directory if it doesn't exist
    mkdir -p "$(dirname "$config_file")"

    cat > "$config_file" << EOF
pcm.!default {
    type hw
    card $card_num
    device $device_num
}

ctl.!default {
    type hw
    card $card_num
    device $device_num
}
EOF
}

# Check if running as root for system-wide configuration
check_root() {
    if [ "$EUID" -ne 0 ] && [ "$1" = "system" ]; then
        echo "Please run as root (use sudo) for system-wide configuration"
        exit 1
    fi
}

# Get list of audio devices
log "Detecting audio devices..."
aplay -l

# Get user input for card number
read -p "Enter the card number you want to use as default: " card_number

# Validate input is a number
if ! [[ "$card_number" =~ ^[0-9]+$ ]]; then
    log "Error: Please enter a valid number"
    exit 1
fi

# Get device number (defaulting to 0 if user just presses enter)
read -p "Enter the device number (default is 0): " device_number
device_number=${device_number:-0}

# Validate device number is a number
if ! [[ "$device_number" =~ ^[0-9]+$ ]]; then
    log "Error: Please enter a valid number"
    exit 1
fi

# Ask for configuration scope
while true; do
    read -p "Do you want to set this configuration system-wide or for current user only? (system/user): " scope
    case $scope in
        system)
            check_root "system"
            config_file="/etc/asound.conf"
            break
            ;;
        user)
            config_file="$HOME/.asoundrc"
            break
            ;;
        *)
            log "Please enter either 'system' or 'user'"
            ;;
    esac
done

# Write the configuration
write_alsa_config "$config_file" "$card_number" "$device_number"

log "Audio configuration updated. Default card $card_number device $device_number set in $config_file"
log "You may need to reboot for changes to take effect"

# Test the audio configuration
log "Testing audio configuration..."
speaker-test -c 2 -t sine -l 1

log "Configuration complete! "
