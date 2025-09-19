#!/bin/bash

echo "SUADAT TERMINAL - AUTOMATED INSTALLATION"
echo "==========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please run as regular user, not root!"
    exit 1
fi

print_status "Starting Suadat Terminal installation..."

# Update system
print_status "Updating package lists..."
sudo apt update

# Install Python and dependencies
print_status "Installing Python 3 and dependencies..."
sudo apt install -y python3 python3-pip python3-tk python3-venv

# Install additional packages
print_status "Installing additional system packages..."
sudo apt install -y git curl wget build-essential

# Install Python packages
print_status "Installing Python packages..."
pip3 install --user requests beautifulsoup4 pandas schedule psutil

# Create application directory
APP_DIR="/opt/suadat-terminal"
print_status "Creating application directory..."
sudo mkdir -p "$APP_DIR"
sudo chown $USER:$USER "$APP_DIR"

# Copy files
print_status "Installing application files..."
cp suadat_terminal.py "$APP_DIR/"
cp launcher.py "$APP_DIR/" 2>/dev/null || true
cp requirements.txt "$APP_DIR/" 2>/dev/null || true

# Create desktop entry
print_status "Creating desktop launcher..."
sudo tee /usr/share/applications/suadat-terminal.desktop > /dev/null << EOF
[Desktop Entry]
Name=Suadat Terminal
Comment=Professional Linux Terminal Emulator with Kali Styling
Exec=python3 $APP_DIR/suadat_terminal.py
Icon=terminal
Type=Application
Categories=Development;System;TerminalEmulator;
Terminal=false
StartupNotify=true
EOF

# Create command line launcher
print_status "Creating command line launcher..."
sudo tee /usr/local/bin/suadat-terminal > /dev/null << 'EOF'
#!/bin/bash
cd "$HOME"
python3 /opt/suadat-terminal/suadat_terminal.py
EOF

sudo chmod +x /usr/local/bin/suadat-terminal

# Set permissions
chmod +x "$APP_DIR"/*.py
sudo chmod +x /usr/share/applications/suadat-terminal.desktop

# Create user data directory
mkdir -p ~/.config/suadat-terminal

# Test installation
print_status "Testing installation..."
if python3 -c "import tkinter; print('tkinter OK')" 2>/dev/null; then
    print_success "tkinter is working"
else
    print_error "tkinter installation failed"
    exit 1
fi

if [ -f "$APP_DIR/suadat_terminal.py" ]; then
    print_success "Application files installed"
else
    print_error "Application installation failedd"
    exit 1
fi

echo ""
print_success "Installation completed successfully!"
echo ""
echo "🎉 How to use:"
echo "   • Search 'Suadat Terminal' in applications menu"
echo "   • Run 'suadat-terminal' from command line"
echo "   • Press Alt+F2 and type 'suadat-terminal'"
echo ""
echo "🛠️  Configuration:"
echo "   • Config files: ~/.config/suadat-terminal/"
echo "   • Installation: $APP_DIR"
echo ""
echo "🚀 Launch now: suadat-terminal"
echo "Follow my on Instagram @suadatbiniqbal "
