import tkinter as tk
from tkinter import scrolledtext, messagebox, Menu
import subprocess
import threading
import os
import datetime
import json
import sys

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

        # Terminal output area
        self.output_text = scrolledtext.ScrolledText(
            main_frame,
            bg=self.bg_color,
            fg=self.text_color,
            font=self.font,
            insertbackground=self.text_color,
            selectbackground='#333333',
            selectforeground=self.text_color,
            wrap=tk.WORD,
            state=tk.DISABLED,
            relief='flat',
            borderwidth=0,
            highlightthickness=0
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, pady=(0, 3))

        # Input area
        input_frame = tk.Frame(main_frame, bg=self.bg_color)
        input_frame.pack(fill=tk.X)

        # Prompt display
        self.prompt_label = tk.Label(
            input_frame,
            text=self.get_prompt(),
            bg=self.bg_color,
            fg=self.prompt_color,
            font=self.font,
            justify=tk.LEFT,
            anchor='w'
        )
        self.prompt_label.pack(side=tk.LEFT)

        # Command input
        self.command_entry = tk.Entry(
            input_frame,
            bg=self.bg_color,
            fg=self.text_color,
            font=self.font,
            insertbackground=self.text_color,
            relief='flat',
            borderwidth=0,
            highlightthickness=0
        )
        self.command_entry.pack(fill=tk.X, side=tk.LEFT, padx=(5, 0))

        # Bind events
        self.command_entry.bind('<Return>', self.execute_command)
        self.command_entry.bind('<Up>', self.previous_command)
        self.command_entry.bind('<Down>', self.next_command)
        self.command_entry.bind('<Tab>', self.tab_completion)
        self.command_entry.bind('<Control-c>', self.interrupt_command)
        self.command_entry.bind('<Control-l>', lambda e: self.clear_terminal())

        # Focus on input
        self.command_entry.focus()

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

    def update_prompt(self):
        """Update prompt display"""
        self.prompt_label.config(text=self.get_prompt())

    def display_welcome(self):
        """Show Kali Linux welcome message"""
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

"""
        self.append_output(welcome, self.text_color)

    def append_output(self, text, color=None):
        """Add text to terminal output"""
        self.output_text.config(state=tk.NORMAL)
        if color:
            tag_name = f"color_{id(color)}"
            self.output_text.tag_config(tag_name, foreground=color)
            self.output_text.insert(tk.END, text, tag_name)
        else:
            self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

    def execute_command(self, event=None):
        """Process and execute commands"""
        command = self.command_entry.get().strip()
        if not command:
            return

        # Add to history
        if command not in self.command_history:
            self.command_history.append(command)
        self.history_index = len(self.command_history)

        # Display command
        self.append_output(f"{self.get_prompt()}{command}\n", self.prompt_color)

        # Clear input
        self.command_entry.delete(0, tk.END)

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
                    self.root.after(0, self.update_prompt)
                else:
                    self.append_output(f"bash: cd: {path}: No such file or directory\n", self.error_color)
            else:
                self.current_dir = os.path.expanduser("~")
                self.root.after(0, self.update_prompt)

        except Exception as e:
            self.append_output(f"bash: cd: {str(e)}\n", self.error_color)

    def clear_terminal(self):
        """Clear terminal screen"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)

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

Navigation:
  ↑/↓ arrows     - Browse command history
  Tab            - Auto-complete (basic)
  Ctrl+C         - Interrupt current command
  Ctrl+L         - Clear screen

Features:
  • Full Linux command support
  • Command history
  • Directory navigation
  • Multi-threaded execution
  • Professional Kali Linux styling

"""
        self.append_output(help_text, self.info_color)

    def show_history(self):
        """Display command history"""
        if not self.command_history:
            self.append_output("No commands in history\n", self.info_color)
            return

        self.append_output("Command History:\n", self.info_color)
        for i, cmd in enumerate(self.command_history[-20:], 1):  # Last 20 commands
            self.append_output(f"{i:3}: {cmd}\n", self.text_color)

    def show_about(self):
        """Show about dialog"""
        about_text = f"""Suadat Terminal v1.0

Professional Linux Terminal Emulator
Built with Python {sys.version.split()[0]} and Tkinter

Features:
• Kali Linux styling
• Full command execution
• Command history
• Professional interface

Created by: Suadat Bin Iqbal
"""
        messagebox.showinfo("About Suadat Terminal", about_text)

    def previous_command(self, event=None):
        """Navigate to previous command"""
        if self.command_history and self.history_index > 0:
            self.history_index -= 1
            self.command_entry.delete(0, tk.END)
            self.command_entry.insert(0, self.command_history[self.history_index])

    def next_command(self, event=None):
        """Navigate to next command"""
        if self.command_history and self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.command_entry.delete(0, tk.END)
            self.command_entry.insert(0, self.command_history[self.history_index])
        elif self.history_index >= len(self.command_history) - 1:
            self.history_index = len(self.command_history)
            self.command_entry.delete(0, tk.END)

    def tab_completion(self, event=None):
        """Basic tab completion"""
        current_text = self.command_entry.get()
        if current_text:
            # Simple file completion
            try:
                if '/' in current_text:
                    path, partial = current_text.rsplit('/', 1)
                    search_dir = os.path.join(self.current_dir, path) if path else self.current_dir
                else:
                    partial = current_text
                    search_dir = self.current_dir

                matches = []
                for item in os.listdir(search_dir):
                    if item.startswith(partial):
                        matches.append(item)

                if len(matches) == 1:
                    # Complete the match
                    if '/' in current_text:
                        completion = current_text.rsplit('/', 1)[0] + '/' + matches[0]
                    else:
                        completion = matches[0]
                    self.command_entry.delete(0, tk.END)
                    self.command_entry.insert(0, completion)

            except:
                pass
        return 'break'

    def interrupt_command(self, event=None):
        """Handle Ctrl+C"""
        self.append_output("^C\n", self.error_color)
        return 'break'

    def increase_font(self):
        """Increase font size"""
        current_size = self.font[1]
        new_font = (self.font[0], min(current_size + 1, 20))
        self.font = new_font
        self.output_text.config(font=new_font)
        self.command_entry.config(font=new_font)
        self.prompt_label.config(font=new_font)

    def decrease_font(self):
        """Decrease font size"""
        current_size = self.font[1]
        new_font = (self.font[0], max(current_size - 1, 8))
        self.font = new_font
        self.output_text.config(font=new_font)
        self.command_entry.config(font=new_font)
        self.prompt_label.config(font=new_font)

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