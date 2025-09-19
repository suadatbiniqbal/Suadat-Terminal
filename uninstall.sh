#!/bin/bash

echo "  SUADAT TERMINAL - UNINSTALLATION"
echo "===================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Confirm uninstallation
read -p "Are you sure you want to uninstall Suadat Terminal? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Uninstallation cancelled."
    exit 0
fi

print_status "Removing Suadat Terminal..."

# Remove application files
print_status "Removing application files..."
sudo rm -rf /opt/suadat-terminal

# Remove desktop entry
print_status "Removing desktop launcher..."
sudo rm -f /usr/share/applications/suadat-terminal.desktop

# Remove command line launcher
print_status "Removing command line launcher..."
sudo rm -f /usr/local/bin/suadat-terminal

# Remove user config (optional)
read -p "Remove user configuration files? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Removing user configuration..."
    rm -rf ~/.config/suadat-terminal
    print_success "User configuration removed"
fi

print_success "Suadat Terminal has been uninstalled successfully!"
echo ""
print_status "Python packages were not removed. To remove them manually:"
echo "pip3 uninstall requests beautifulsoup4 pandas schedule psutil"
