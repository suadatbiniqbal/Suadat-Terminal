#!/usr/bin/env python3
"""
Suadat Terminal Launcher
Handles startup and error checking
"""
#follow me on instagram @suadatbiniqbal

import sys
import os
import subprocess
import tkinter as tk
from tkinter import messagebox

def check_dependencies():
    """Check if all dependencies are installed"""
    missing = []

    try:
        import tkinter
    except ImportError:
        missing.append("python3-tk")

    if missing:
        return missing
    return None

def show_error(message):
    """Show error message"""
    try:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Suadat Terminal Error", message)
    except:
        print(f"Error: {message}")

def main():
    """Main launcher"""
    # Check dependencies
    missing = check_dependencies()
    if missing:
        error_msg = f"Missing dependencies: {', '.join(missing)}\n\nPlease run: sudo apt install {' '.join(missing)}"
        show_error(error_msg)
        return 1

    # Launch terminal
    try:
        from suadat_terminal import main as terminal_main
        terminal_main()
    except ImportError:
        try:
            # Try to run as subprocess if import fails
            script_dir = os.path.dirname(os.path.abspath(__file__))
            terminal_script = os.path.join(script_dir, 'suadat_terminal.py')
            subprocess.run([sys.executable, terminal_script])
        except Exception as e:
            show_error(f"Failed to launch terminal: {str(e)}")
            return 1
    except Exception as e:
        show_error(f"Terminal error: {str(e)}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
