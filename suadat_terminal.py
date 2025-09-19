import tkinter as tk
from tkinter import scrolledtext, messagebox, Menu
import subprocess
import threading
import os
import datetime
import json
import sys
import requests
import base64
from io import BytesIO
from urllib.parse import urlparse
import time

class SuadatTerminal:
    def __init__(self, root):
        self.root = root
        self.root.title("Suadat Terminal - Kali Linux Style")
        self.root.geometry("900x700")
        self.root.configure(bg='#000000')

        # Set window icon and properties
        self.root.resizable(True, True)
        self.root.minsize(600, 400)

        # Kali Linux terminal colors
        self.bg_color = '#000000'          # Pure black
        self.text_color = '#ffffff'        # White text
        self.prompt_color = '#00ff00'      # Green prompt
        self.error_color = '#ff0000'       # Red errors
        self.info_color = '#00ffff'        # Cyan info
        self.font = ('DejaVu Sans Mono', 11)

        # Terminal state
        self.current_dir = os.getcwd()
        self.command_history = []
        self.history_index = -1
        self.config_file = 'terminal_config.json'
        self.current_command = ""
        self.cursor_position = 0

        # Animation variables
        self.animation_speed = 50
        self.typing_animation = False

        # Load configuration
        self.load_config()

        # Create GUI
        self.create_menu()
        self.create_widgets()
        self.display_welcome()

        # Bind window events
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_menu(self):
        """Create menu bar"""
        menubar = Menu(self.root, bg=self.bg_color, fg=self.text_color)
        self.root.config(menu=menubar)

        # File menu
        file_menu = Menu(menubar, tearoff=0, bg=self.bg_color, fg=self.text_color)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Terminal", command=self.new_terminal)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)

        # View menu
        view_menu = Menu(menubar, tearoff=0, bg=self.bg_color, fg=self.text_color)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Clear Screen", command=self.clear_terminal)
        view_menu.add_command(label="Font Size +", command=self.increase_font)
        view_menu.add_command(label="Font Size -", command=self.decrease_font)

        # Help menu
        help_menu = Menu(menubar, tearoff=0, bg=self.bg_color, fg=self.text_color)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Commands", command=self.show_help)
        help_menu.add_command(label="About", command=self.show_about)

    def create_widgets(self):
        """Create main terminal interface"""
        # Main container
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)

        # Terminal output area with embedded input
        self.terminal_text = scrolledtext.ScrolledText(
            main_frame,
            bg=self.bg_color,
            fg=self.text_color,
            font=self.font,
            insertbackground=self.text_color,
            selectbackground='#333333',
            selectforeground=self.text_color,
            wrap=tk.WORD,
            relief='flat',
            borderwidth=0,
            highlightthickness=0,
            insertwidth=2
        )
        self.terminal_text.pack(fill=tk.BOTH, expand=True)

        # Bind events for terminal-like behavior
        self.terminal_text.bind('<Key>', self.on_key_press)
        self.terminal_text.bind('<Button-1>', self.on_click)
        self.terminal_text.bind('<Up>', self.previous_command)
        self.terminal_text.bind('<Down>', self.next_command)
        self.terminal_text.bind('<Control-c>', self.interrupt_command)
        self.terminal_text.bind('<Control-l>', lambda e: self.clear_terminal())
        
        # Focus on terminal
        self.terminal_text.focus()

        # Initialize prompt
        self.show_prompt()

    def get_prompt(self):
        """Generate Kali-style prompt"""
        user = os.getenv('USER', 'suadat')
        hostname = 'kali'
        path = self.get_short_path()
        return f"┌──({user}@{hostname})-[{path}]\n└─$ "

    def get_short_path(self):
        """Get shortened path for prompt"""
        path = self.current_dir
        home = os.path.expanduser("~")
        if path.startswith(home):
            path = "~" + path[len(home):]
        return path

    def show_prompt(self):
        """Display prompt and position cursor"""
        prompt = self.get_prompt()
        self.terminal_text.insert(tk.END, prompt)
        self.terminal_text.mark_set("prompt_end", tk.END)
        self.terminal_text.see(tk.END)

    def on_key_press(self, event):
        """Handle key presses for terminal-like behavior"""
        # Get current cursor position
        current_pos = self.terminal_text.index(tk.INSERT)
        prompt_pos = self.terminal_text.index("prompt_end")
        
        # Only allow editing after the prompt
        if self.terminal_text.compare(current_pos, "<", prompt_pos):
            self.terminal_text.mark_set(tk.INSERT, tk.END)
            return "break"

        if event.keysym == 'Return':
            # Get command from current line
            command_line = self.terminal_text.get("prompt_end", tk.END).strip()
            if command_line:
                self.execute_command(command_line)
            else:
                self.terminal_text.insert(tk.END, "\n")
                self.show_prompt()
            return "break"
        
        elif event.keysym == 'BackSpace':
            # Prevent deletion before prompt
            if self.terminal_text.compare(tk.INSERT, "<=", prompt_pos):
                return "break"
        
        elif event.keysym == 'Left':
            # Prevent moving cursor before prompt
            if self.terminal_text.compare(tk.INSERT, "<=", prompt_pos):
                return "break"
                
        elif event.keysym == 'Home':
            # Move to beginning of command (after prompt)
            self.terminal_text.mark_set(tk.INSERT, prompt_pos)
            return "break"

        return None

    def on_click(self, event):
        """Handle mouse clicks"""
        # Ensure cursor stays after prompt
        prompt_pos = self.terminal_text.index("prompt_end")
        click_pos = self.terminal_text.index(f"@{event.x},{event.y}")
        
        if self.terminal_text.compare(click_pos, "<", prompt_pos):
            self.terminal_text.mark_set(tk.INSERT, tk.END)
            return "break"

    def display_welcome(self):
        """Show Kali Linux welcome message with typing animation"""
        welcome = f"""Suadat Terminal 6.1.0-kali7-amd64 #1 SMP PREEMPT_DYNAMIC 

The programs included with the Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

idk GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.

Last login: {datetime.datetime.now().strftime('%a %b %d %H:%M:%S %Y')} from 192.168.1.100

┌──(suadat@kali)-[~]
└─$ Welcome to Suadat Terminal - Professional Linux Terminal Emulator
└─$ Type 'help' for available commands
└─$ Use 'g <image_url>' to display image information with animations

"""
        self.animate_text(welcome, self.text_color)

    def animate_text(self, text, color=None, delay=20):
        """Animate text typing effect"""
        self.typing_animation = True
        
        def type_char(index=0):
            if index < len(text) and self.typing_animation:
                char = text[index]
                if color:
                    tag_name = f"color_{id(color)}"
                    self.terminal_text.tag_config(tag_name, foreground=color)
                    self.terminal_text.insert(tk.END, char, tag_name)
                else:
                    self.terminal_text.insert(tk.END, char)
                
                self.terminal_text.see(tk.END)
                self.root.after(delay, lambda: type_char(index + 1))
            elif index >= len(text):
                self.typing_animation = False
                self.show_prompt()
        
        type_char()

    def append_output(self, text, color=None):
        """Add text to terminal output"""
        if color:
            tag_name = f"color_{id(color)}"
            self.terminal_text.tag_config(tag_name, foreground=color)
            self.terminal_text.insert(tk.END, text, tag_name)
        else:
            self.terminal_text.insert(tk.END, text)
        self.terminal_text.see(tk.END)

    def execute_command(self, command):
        """Process and execute commands"""
        # Add to history
        if command not in self.command_history:
            self.command_history.append(command)
        self.history_index = len(self.command_history)

        # Move to new line
        self.terminal_text.insert(tk.END, "\n")

        # Check for image command
        if command.startswith('g '):
            image_url = command[2:].strip()
            self.load_image_info_with_animation(image_url)
            return

        # Execute in thread
        thread = threading.Thread(target=self.run_command, args=(command,))
        thread.daemon = True
        thread.start()

    def run_command(self, command):
        """Execute the actual command"""
        try:
            # Built-in commands
            if command.lower() in ['exit', 'quit']:
                self.root.quit()
                return
            elif command.lower() == 'clear':
                self.clear_terminal()
                return
            elif command.lower() == 'help':
                self.show_help()
                return
            elif command.startswith('cd '):
                self.change_directory(command[3:].strip())
                return
            elif command == 'cd':
                self.change_directory(os.path.expanduser("~"))
                return
            elif command == 'history':
                self.show_history()
                return

            # System commands
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.current_dir,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.stdout:
                self.append_output(result.stdout, self.text_color)
            if result.stderr:
                self.append_output(result.stderr, self.error_color)

        except subprocess.TimeoutExpired:
            self.append_output("Command timed out after 30 seconds\n", self.error_color)
        except FileNotFoundError:
            self.append_output(f"bash: {command.split()[0]}: command not found\n", self.error_color)
        except Exception as e:
            self.append_output(f"Error: {str(e)}\n", self.error_color)
        
        finally:
            # Show new prompt after command execution
            self.root.after(0, self.show_prompt)

    def load_image_info_with_animation(self, url):
        """Load and display image information with animations (no PIL required)"""
        def load_in_thread():
            try:
                # Show loading animation
                loading_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
                loading_text = "Downloading image "
                
                def animate_loading(index=0, count=0):
                    if count < 15:  # Show loading for ~1.5 seconds
                        char = loading_chars[index % len(loading_chars)]
                        # Clear previous loading text
                        current_line = self.terminal_text.get("end-1l linestart", "end-1l lineend")
                        if "Downloading image" in current_line:
                            self.terminal_text.delete("end-1l linestart", "end-1l lineend")
                        
                        self.append_output(f"{loading_text}{char}\n", self.info_color)
                        self.root.after(100, lambda: animate_loading(index + 1, count + 1))
                    else:
                        # Actually load the image info
                        self.get_image_info(url)
                
                animate_loading()
                
            except Exception as e:
                self.append_output(f"Error loading image: {str(e)}\n", self.error_color)
                self.show_prompt()

        thread = threading.Thread(target=load_in_thread)
        thread.daemon = True
        thread.start()

    def get_image_info(self, url):
        """Get image information without PIL"""
        try:
            # Validate URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme:
                url = 'https://' + url

            # Download image headers only
            response = requests.head(url, timeout=10)
            response.raise_for_status()

            # Clear loading text
            current_line = self.terminal_text.get("end-1l linestart", "end-1l lineend")
            if "Downloading image" in current_line:
                self.terminal_text.delete("end-1l linestart", "end-1l lineend")

            # Display image info with animation
            self.display_image_info_with_animation(url, response.headers)

        except requests.RequestException as e:
            self.append_output(f"Failed to access image: {str(e)}\n", self.error_color)
            self.show_prompt()
        except Exception as e:
            self.append_output(f"Error processing image: {str(e)}\n", self.error_color)
            self.show_prompt()

    def display_image_info_with_animation(self, url, headers):
        """Display image information with cool ASCII art"""
        
        # ASCII art for image
        ascii_art = """
╭─────────────────────────────────────────╮
│  🖼️  IMAGE LOADED SUCCESSFULLY  🖼️       │
├─────────────────────────────────────────┤
│                                         │
│    ██████╗ ██╗██╗  ██╗███████╗██╗       │
│    ██╔══██╗██║╚██╗██╔╝██╔════╝██║       │
│    ██████╔╝██║ ╚███╔╝ █████╗  ██║       │
│    ██╔═══╝ ██║ ██╔██╗ ██╔══╝  ██║       │
│    ██║     ██║██╔╝ ██╗███████╗███████╗   │
│    ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝   │
│                                         │
╰─────────────────────────────────────────╯
"""
        
        # Animate ASCII art
        def animate_art():
            lines = ascii_art.strip().split('\n')
            for i, line in enumerate(lines):
                self.append_output(line + "\n", self.info_color)
                self.root.update()
                time.sleep(0.05)  # Small delay for animation effect
        
        animate_art()
        
        # Display image details
        info_text = f"""
Image URL: {url}
Content-Type: {headers.get('content-type', 'Unknown')}
Content-Length: {headers.get('content-length', 'Unknown')} bytes
Server: {headers.get('server', 'Unknown')}
Last-Modified: {headers.get('last-modified', 'Unknown')}

✨ Image information loaded successfully! ✨
Note: Install python3-pil.imagetk for full image display support.

"""
        self.animate_text(info_text, self.text_color, delay=10)

    def change_directory(self, path):
        """Handle directory changes"""
        try:
            if path:
                new_path = os.path.expanduser(path)
                if not os.path.isabs(new_path):
                    new_path = os.path.join(self.current_dir, new_path)
                new_path = os.path.normpath(new_path)

                if os.path.exists(new_path) and os.path.isdir(new_path):
                    self.current_dir = new_path
                else:
                    self.append_output(f"bash: cd: {path}: No such file or directory\n", self.error_color)
            else:
                self.current_dir = os.path.expanduser("~")

        except Exception as e:
            self.append_output(f"bash: cd: {str(e)}\n", self.error_color)
        
        finally:
            self.show_prompt()

    def clear_terminal(self):
        """Clear terminal screen"""
        self.terminal_text.delete(1.0, tk.END)
        self.show_prompt()

    def show_help(self):
        """Display help information"""
        help_text = """
Suadat Terminal - Command Reference
═══════════════════════════════════

Built-in Commands:
  help           - Show this help message
  clear          - Clear terminal screen
  cd [path]      - Change directory
  history        - Show command history
  exit/quit      - Exit terminal
  g <url>        - Display image information with animations

System Commands:
  ls             - List directory contents
  pwd            - Print working directory
  cat [file]     - Display file contents
  grep [pattern] - Search for patterns
  find [path]    - Find files and directories
  ps             - Show running processes
  top            - Display system processes
  df -h          - Show disk usage
  free -h        - Show memory usage

Image Commands:
  g https://example.com/image.jpg  - Get image info
  g domain.com/pic.png            - Auto-add https protocol

Navigation:
  ↑/↓ arrows     - Browse command history
  Home           - Move to start of command
  Ctrl+C         - Interrupt current command
  Ctrl+L         - Clear screen

Features:
  • Full Linux command support
  • Animated image information display
  • Real-time typing animations
  • Command history with arrow navigation
  • Professional Kali Linux styling
  • Thread-safe command execution

Installation Note:
  For full image display support, install:
  sudo apt-get install python3-pil python3-pil.imagetk

"""
        self.animate_text(help_text, self.info_color, delay=5)

    def show_history(self):
        """Display command history"""
        if not self.command_history:
            self.append_output("No commands in history\n", self.info_color)
            self.show_prompt()
            return

        self.append_output("Command History:\n", self.info_color)
        for i, cmd in enumerate(self.command_history[-20:], 1):  # Last 20 commands
            self.append_output(f"{i:3}: {cmd}\n", self.text_color)
        self.show_prompt()

    def show_about(self):
        """Show about dialog"""
        about_text = f"""Suadat Terminal v2.0

Professional Linux Terminal Emulator
Built with Python {sys.version.split()[0]} and Tkinter

Features:
• Kali Linux styling
• Full command execution  
• Animated image information
• Command history
• Real-time animations
• Professional interface

Created by: Suadat Bin Iqbal
"""
        messagebox.showinfo("About Suadat Terminal", about_text)

    def previous_command(self, event=None):
        """Navigate to previous command"""
        if self.command_history and self.history_index > 0:
            self.history_index -= 1
            # Clear current command line
            self.terminal_text.delete("prompt_end", tk.END)
            # Insert previous command
            self.terminal_text.insert(tk.END, self.command_history[self.history_index])
        return "break"

    def next_command(self, event=None):
        """Navigate to next command"""
        if self.command_history and self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            # Clear current command line
            self.terminal_text.delete("prompt_end", tk.END)
            # Insert next command
            self.terminal_text.insert(tk.END, self.command_history[self.history_index])
        elif self.history_index >= len(self.command_history) - 1:
            self.history_index = len(self.command_history)
            # Clear current command line
            self.terminal_text.delete("prompt_end", tk.END)
        return "break"

    def interrupt_command(self, event=None):
        """Handle Ctrl+C"""
        self.append_output("^C\n", self.error_color)
        self.show_prompt()
        return "break"

    def increase_font(self):
        """Increase font size"""
        current_size = self.font[1]
        new_font = (self.font[0], min(current_size + 1, 20))
        self.font = new_font
        self.terminal_text.config(font=new_font)

    def decrease_font(self):
        """Decrease font size"""
        current_size = self.font[1]
        new_font = (self.font[0], max(current_size - 1, 8))
        self.font = new_font
        self.terminal_text.config(font=new_font)

    def new_terminal(self):
        """Open new terminal window"""
        new_root = tk.Toplevel()
        SuadatTerminal(new_root)

    def load_config(self):
        """Load terminal configuration"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.font = tuple(config.get('font', self.font))
        except:
            pass

    def save_config(self):
        """Save terminal configuration"""
        try:
            config = {
                'font': list(self.font),
                'current_dir': self.current_dir,
                'history': self.command_history[-50:]  # Save last 50 commands
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
    """Main application entry point"""
    root = tk.Tk()
    app = SuadatTerminal(root)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
#follow me on instagram @suadatbiniqbal
