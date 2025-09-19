import tkinter as tk
from tkinter import scrolledtext, messagebox, Menu
import subprocess
import threading
import os
import datetime
import json
import sys
import requests
import time
from urllib.parse import urlparse

class HyprlandTerminal:
    def __init__(self, root):
        self.root = root
        self.root.title("Hyprland Terminal - Suadat Edition")
        self.root.geometry("1000x700")
        
        # Hyprland color scheme (Catppuccin-inspired)
        self.colors = {
            'bg': '#1e1e2e',           # Dark background
            'surface': '#313244',      # Surface color
            'text': '#cdd6f4',         # White-blue text
            'subtext': '#bac2de',      # Subtext
            'accent': '#f38ba8',       # Pink accent
            'green': '#a6e3a1',        # Green
            'blue': '#89b4fa',         # Blue  
            'yellow': '#f9e2af',       # Yellow
            'red': '#f38ba8',          # Red
            'purple': '#cba6f7',       # Purple
            'orange': '#fab387',       # Orange
            'cyan': '#94e2d5'          # Cyan
        }
        
        self.root.configure(bg=self.colors['bg'])
        self.root.resizable(True, True)
        self.root.minsize(800, 500)

        # Terminal state
        self.current_dir = os.getcwd()
        self.command_history = []
        self.history_index = -1
        self.config_file = 'hyprland_terminal_config.json'
        
        # Font settings
        self.font_family = 'JetBrainsMono Nerd Font'
        self.font_size = 11
        self.font = (self.font_family, self.font_size)

        # Load configuration
        self.load_config()

        # Create GUI
        self.create_widgets()
        self.display_welcome()
        self.show_prompt()

        # Bind events
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.bind('<Control-c>', self.interrupt_command)
        self.root.bind('<Control-l>', lambda e: self.clear_terminal())

    def create_widgets(self):
        """Create modern Hyprland-style interface"""
        # Main container with rounded effect
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header bar
        header = tk.Frame(main_frame, bg=self.colors['surface'], height=40)
        header.pack(fill=tk.X, pady=(0, 10))
        header.pack_propagate(False)

        # Terminal title
        title_label = tk.Label(
            header, 
            text="   Hyprland Terminal", 
            bg=self.colors['surface'], 
            fg=self.colors['accent'],
            font=(self.font_family, 12, 'bold'),
            anchor='w'
        )
        title_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=8)

        # Control buttons
        controls_frame = tk.Frame(header, bg=self.colors['surface'])
        controls_frame.pack(side=tk.RIGHT, padx=10, pady=8)

        for color, text in [(self.colors['red'], '●'), (self.colors['yellow'], '●'), (self.colors['green'], '●')]:
            btn = tk.Label(
                controls_frame, 
                text=text, 
                fg=color, 
                bg=self.colors['surface'], 
                font=('Arial', 14)
            )
            btn.pack(side=tk.LEFT, padx=2)

        # Terminal container
        terminal_frame = tk.Frame(main_frame, bg=self.colors['surface'])
        terminal_frame.pack(fill=tk.BOTH, expand=True)

        # Output area
        self.output_text = scrolledtext.ScrolledText(
            terminal_frame,
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=self.font,
            insertbackground=self.colors['accent'],
            selectbackground=self.colors['surface'],
            selectforeground=self.colors['text'],
            wrap=tk.WORD,
            state=tk.DISABLED,
            relief='flat',
            borderwidth=0,
            highlightthickness=0
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Input frame
        input_frame = tk.Frame(terminal_frame, bg=self.colors['bg'])
        input_frame.pack(fill=tk.X, padx=15, pady=(0, 15))

        # Command input
        self.command_var = tk.StringVar()
        self.command_entry = tk.Entry(
            input_frame,
            textvariable=self.command_var,
            bg=self.colors['surface'],
            fg=self.colors['text'],
            font=self.font,
            insertbackground=self.colors['accent'],
            relief='flat',
            borderwidth=0,
            highlightthickness=2,
            highlightcolor=self.colors['accent'],
            highlightbackground=self.colors['surface']
        )
        self.command_entry.pack(fill=tk.X, ipady=8)

        # Bind input events [web:40][web:41]
        self.command_entry.bind('<Return>', self.execute_command)
        self.command_entry.bind('<Up>', self.previous_command)
        self.command_entry.bind('<Down>', self.next_command)
        self.command_entry.bind('<Tab>', self.tab_completion)
        self.command_entry.bind('<Control-c>', self.interrupt_command)
        self.command_entry.bind('<KeyRelease>', self.on_key_release)

        # Focus on input
        self.command_entry.focus()

        # Status bar
        status_frame = tk.Frame(main_frame, bg=self.colors['surface'], height=25)
        status_frame.pack(fill=tk.X, pady=(5, 0))
        status_frame.pack_propagate(False)

        self.status_label = tk.Label(
            status_frame,
            text=f"  {self.current_dir}",
            bg=self.colors['surface'],
            fg=self.colors['subtext'],
            font=(self.font_family, 9),
            anchor='w'
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=2)

    def get_prompt(self):
        """Generate Hyprland-style prompt"""
        user = os.getenv('USER', 'suadat')
        hostname = 'hyprland'
        path = self.get_short_path()
        return f"╭─ {user}@{hostname} in {path}\n╰─λ "

    def get_short_path(self):
        """Get shortened path"""
        path = self.current_dir
        home = os.path.expanduser("~")
        if path.startswith(home):
            path = "~" + path[len(home):]
        return path

    def show_prompt(self):
        """Show prompt"""
        prompt = self.get_prompt()
        self.append_output(prompt, self.colors['green'])

    def display_welcome(self):
        """Show Hyprland welcome with animations"""
        welcome = f"""
╭─────────────────────────────────────────────────────────╮
        
│  ██████  ██    ██  █████  ██████   █████  ████████ │
│  ██      ██    ██ ██   ██ ██   ██ ██   ██    ██    │
│  ███████ ██    ██ ███████ ██   ██ ███████    ██    │
│       ██ ██    ██ ██   ██ ██   ██ ██   ██    ██    │
│  ███████  ██████  ██   ██ ██████  ██   ██    ██    │
│  Terminal v3.0 - Wayland Compositor Terminal
│  Last login: {datetime.datetime.now().strftime('%a %b %d %H:%M:%S %Y')}
│  
│  Available commands:
│    help     - Show help
│    clear    - Clear screen  
│    neofetch - System info
│    weather  - Get weather
│    crypto   - Crypto prices
│    matrix   - Matrix effect
│    tree     - File tree
│    htop     - System monitor (fake)
╰─────────────────────────────────────────────────────────

"""
        self.animate_text(welcome, self.colors['cyan'], 15)

    def animate_text(self, text, color, delay=30):
        """Animate text typing"""
        lines = text.split('\n')
        
        def type_line(line_index=0):
            if line_index < len(lines):
                line = lines[line_index] + '\n'
                for i, char in enumerate(line):
                    self.root.after(delay * i, lambda c=char: self.append_output(c, color))
                
                self.root.after(delay * len(line), lambda: type_line(line_index + 1))
        
        type_line()

    def append_output(self, text, color=None):
        """Add text to output"""
        self.output_text.config(state=tk.NORMAL)
        if color:
            tag_name = f"color_{color}"
            self.output_text.tag_config(tag_name, foreground=color)
            self.output_text.insert(tk.END, text, tag_name)
        else:
            self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

    def on_key_release(self, event):
        """Handle real-time input feedback [web:46][web:49]"""
        current_text = self.command_var.get()
        if current_text:
            # Change input color based on command validity
            if self.is_valid_command(current_text.split()[0]):
                self.command_entry.config(fg=self.colors['green'])
            else:
                self.command_entry.config(fg=self.colors['text'])
        else:
            self.command_entry.config(fg=self.colors['text'])

    def is_valid_command(self, cmd):
        """Check if command is valid"""
        builtin_commands = ['help', 'clear', 'cd', 'exit', 'quit', 'history', 'neofetch', 'weather', 'crypto', 'matrix', 'tree', 'htop']
        return cmd in builtin_commands or self.command_exists(cmd)

    def command_exists(self, cmd):
        """Check if system command exists"""
        try:
            subprocess.run(['which', cmd], capture_output=True, check=True)
            return True
        except:
            return False

    def execute_command(self, event=None):
        """Execute command [web:40]"""
        command = self.command_var.get().strip()
        if not command:
            self.append_output('\n')
            self.show_prompt()
            return

        # Add to history
        if command not in self.command_history:
            self.command_history.append(command)
        self.history_index = len(self.command_history)

        # Clear input
        self.command_var.set('')
        self.command_entry.config(fg=self.colors['text'])

        # Show command
        self.append_output(f"{command}\n", self.colors['yellow'])

        # Execute
        if command in ['exit', 'quit']:
            self.root.quit()
        elif command == 'clear':
            self.clear_terminal()
        elif command == 'help':
            self.show_help()
        elif command.startswith('cd '):
            self.change_directory(command[3:].strip())
        elif command == 'cd':
            self.change_directory(os.path.expanduser("~"))
        elif command == 'history':
            self.show_history()
        elif command == 'neofetch':
            self.show_neofetch()
        elif command == 'weather':
            self.show_weather()
        elif command == 'crypto':
            self.show_crypto()
        elif command == 'matrix':
            self.matrix_effect()
        elif command == 'tree':
            self.show_tree()
        elif command == 'htop':
            self.fake_htop()
        else:
            # System command
            thread = threading.Thread(target=self.run_system_command, args=(command,))
            thread.daemon = True
            thread.start()

    def run_system_command(self, command):
        """Run system command"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.current_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.stdout:
                self.append_output(result.stdout, self.colors['text'])
            if result.stderr:
                self.append_output(result.stderr, self.colors['red'])
                
        except subprocess.TimeoutExpired:
            self.append_output("⚠ Command timed out\n", self.colors['red'])
        except Exception as e:
            self.append_output(f"⚠ Error: {str(e)}\n", self.colors['red'])
        finally:
            self.root.after(0, self.show_prompt)

    def show_neofetch(self):
        """Show system info"""
        import platform
        info = f"""
╭─ System Information
├─ OS: {platform.system()} {platform.release()}
├─ Kernel: {platform.version().split()[0]}
├─ Architecture: {platform.machine()}
├─ Python: {platform.python_version()}
├─ Terminal: Hyprland Terminal v3.0
├─ Shell: Built-in Python Shell
├─ DE: Hyprland (Wayland)
╰─ Uptime: {datetime.datetime.now().strftime('%H:%M:%S')}

"""
        self.animate_text(info, self.colors['blue'], 10)
        self.root.after(2000, self.show_prompt)

    def show_weather(self):
        """Get weather info (mock)"""
        weather_info = """
╭─ Weather Information
├─ Location: Your City
├─ Temperature: 22°C
├─ Condition: Partly Cloudy ⛅
├─ Humidity: 65%
├─ Wind: 12 km/h
╰─ Pressure: 1013 hPa

"""
        self.animate_text(weather_info, self.colors['cyan'], 20)
        self.root.after(1500, self.show_prompt)

    def show_crypto(self):
        """Show crypto prices (mock)"""
        crypto_info = """
╭─ Cryptocurrency Prices
├─ ₿ Bitcoin: $45,230.50 📈
├─ Ξ Ethereum: $3,120.75 📊  
├─ ⚡ Lightning: $0.0012 ⚡
├─ 🔸 Cardano: $1.25 💎
╰─ Last updated: just now

"""
        self.animate_text(crypto_info, self.colors['yellow'], 25)
        self.root.after(2000, self.show_prompt)

    def matrix_effect(self):
        """Matrix digital rain effect"""
        matrix_chars = "01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZアイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン"
        
        def animate_matrix(count=0):
            if count < 50:  # 5 seconds of animation
                line = ""
                for _ in range(40):
                    import random
                    line += random.choice(matrix_chars)
                self.append_output(line + "\n", self.colors['green'])
                self.root.after(100, lambda: animate_matrix(count + 1))
            else:
                self.append_output("\n🔴 Connection terminated.\n\n", self.colors['red'])
                self.show_prompt()
        
        self.append_output("🔵 Entering the Matrix...\n", self.colors['green'])
        animate_matrix()

    def show_tree(self):
        """Show directory tree"""
        tree_output = """
📁 Current Directory Structure:
├── 📄 suadat_terminal.py
├── 📄 config.json
├── 📁 assets/
│   ├── 🖼️ icon.png  
│   └── 🎨 themes/
├── 📁 scripts/
│   ├── 📄 install.sh
│   └── 📄 update.sh
└── 📄 README.md

"""
        self.animate_text(tree_output, self.colors['purple'], 30)
        self.root.after(2000, self.show_prompt)

    def fake_htop(self):
        """Fake system monitor"""
        htop_display = """
╭─ System Monitor (htop style)
├─ CPU:  ████████░░ 78% 
├─ MEM:  ██████░░░░ 62%
├─ SWP:  ██░░░░░░░░ 15%
├─ 
├─ PID  USER      %CPU %MEM COMMAND
├─ 1234 suadat    25.3  8.2 hyprland-terminal
├─ 5678 suadat    15.8  4.1 python3
├─ 9012 suadat     8.4  2.7 bash
├─ 3456 root       5.2  1.8 systemd
╰─ Press 'q' to quit (simulation)

"""
        self.animate_text(htop_display, self.colors['orange'], 20)
        self.root.after(3000, self.show_prompt)

    def show_help(self):
        """Show help"""
        help_text = f"""
╭─ Hyprland Terminal Help
├─ Built-in Commands:
│  ├─ help      - Show this help
│  ├─ clear     - Clear terminal
│  ├─ cd <dir>  - Change directory  
│  ├─ history   - Command history
│  ├─ exit/quit - Exit terminal
│  ├─ neofetch  - System information
│  ├─ weather   - Weather info
│  ├─ crypto    - Crypto prices
│  ├─ matrix    - Matrix effect
│  ├─ tree      - Directory tree
│  └─ htop      - System monitor
├─
├─ Features:
│  ├─ Real-time command validation
│  ├─ Command history (↑/↓)
│  ├─ Tab completion
│  ├─ Modern Hyprland styling
│  ├─ Animated text effects
│  └─ Thread-safe execution
├─
├─ Shortcuts:
│  ├─ Ctrl+C - Interrupt
│  ├─ Ctrl+L - Clear screen
│  └─ Tab    - Auto-complete
╰─ Created by @suadatbiniqbal

"""
        self.animate_text(help_text, self.colors['blue'], 10)
        self.root.after(4000, self.show_prompt)

    def show_history(self):
        """Show command history"""
        if not self.command_history:
            self.append_output("No commands in history\n", self.colors['subtext'])
            self.show_prompt()
            return

        self.append_output("╭─ Command History\n", self.colors['green'])
        for i, cmd in enumerate(self.command_history[-15:], 1):
            self.append_output(f"├─ {i:2}: {cmd}\n", self.colors['text'])
        self.append_output("╰─ End of history\n\n", self.colors['green'])
        self.show_prompt()

    def change_directory(self, path):
        """Change directory"""
        try:
            if path:
                new_path = os.path.expanduser(path)
                if not os.path.isabs(new_path):
                    new_path = os.path.join(self.current_dir, new_path)
                new_path = os.path.normpath(new_path)

                if os.path.exists(new_path) and os.path.isdir(new_path):
                    self.current_dir = new_path
                    self.status_label.config(text=f"  {self.current_dir}")
                    self.append_output(f"📁 Changed to: {self.get_short_path()}\n", self.colors['green'])
                else:
                    self.append_output(f"❌ Directory not found: {path}\n", self.colors['red'])
            else:
                self.current_dir = os.path.expanduser("~")
                self.status_label.config(text=f"  {self.current_dir}")
                self.append_output(f"🏠 Changed to home directory\n", self.colors['green'])

        except Exception as e:
            self.append_output(f"❌ Error: {str(e)}\n", self.colors['red'])
        
        self.show_prompt()

    def clear_terminal(self):
        """Clear terminal"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.show_prompt()

    def previous_command(self, event=None):
        """Previous command [web:40]"""
        if self.command_history and self.history_index > 0:
            self.history_index -= 1
            self.command_var.set(self.command_history[self.history_index])
            self.command_entry.icursor(tk.END)
        return "break"

    def next_command(self, event=None):
        """Next command [web:40]"""
        if self.command_history and self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.command_var.set(self.command_history[self.history_index])
            self.command_entry.icursor(tk.END)
        elif self.history_index >= len(self.command_history) - 1:
            self.history_index = len(self.command_history)
            self.command_var.set('')
        return "break"

    def tab_completion(self, event=None):
        """Tab completion"""
        current_text = self.command_var.get()
        cursor_pos = self.command_entry.index(tk.INSERT)
        
        if current_text:
            # Simple completion for common commands
            commands = ['help', 'clear', 'cd', 'ls', 'pwd', 'cat', 'grep', 'find', 'neofetch', 'weather', 'crypto', 'matrix', 'tree', 'htop']
            matches = [cmd for cmd in commands if cmd.startswith(current_text)]
            
            if len(matches) == 1:
                self.command_var.set(matches[0])
                self.command_entry.icursor(tk.END)
        
        return "break"

    def interrupt_command(self, event=None):
        """Interrupt command"""
        self.append_output("\n^C\n", self.colors['red'])
        self.command_var.set('')
        self.show_prompt()
        return "break"

    def load_config(self):
        """Load configuration"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.font_size = config.get('font_size', self.font_size)
                    self.font = (self.font_family, self.font_size)
        except:
            pass

    def save_config(self):
        """Save configuration"""
        try:
            config = {
                'font_size': self.font_size,
                'current_dir': self.current_dir,
                'history': self.command_history[-50:]
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except:
            pass

    def on_closing(self):
        """Handle window closing"""
        self.save_config()
        self.root.destroy()

def main():
    """Main entry point"""
    root = tk.Tk()
    app = HyprlandTerminal(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
#follow me on instagram @suadatbiniqbal
