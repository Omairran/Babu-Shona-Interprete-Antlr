import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import subprocess
import threading
import re
import pygame.mixer
import os

class BabuIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("Babu IDE")
        self.root.config(bg="#1c1c1c")
        self.root.geometry("800x600")

        # Initialize sound system
        pygame.mixer.init()
        self.is_muted = False
        self.audio_files = {
            'dark_mode': 'audio/dark_mode.mp3',
            'error': 'audio/error.mp3',
            'exit': 'audio/exit.mp3',
            'light_mode': 'audio/light_mode.mp3',
            'new': 'audio/new.mp3',
            'open': 'audio/open.mp3',
            'save': 'audio/save.mp3',
            'save_as': 'audio/save_as.mp3',
            'input': 'audio/input.mp3',
            'run': 'audio/run.mp3'  # Added run sound
        }

        # Current file name
        self.current_file = None
        self.waiting_for_input = False

        # Define keywords and colors for light and dark modes
        self.keywords = {
            "dekho babu": {"dark": "#FFF176", "light": "#FFC107"},
            "mela babu": {"dark": "#FFB74D", "light": "#FF4500"},
            "bolo shona": {"dark": "#81D4FA", "light": "#1E90FF"},
            "agar babu": {"dark": "#C8E6C9", "light": "#32CD32"},
            "lekin babu": {"dark": "#C8E6C9", "light": "#32CD32"},
            "magar shona": {"dark": "#FFCC80", "light": "#FFA500"},
            "chalo babu": {"dark": "#F8BBD0", "light": "#FF69B4"},
            "Shona": {"dark": "#E57373", "light": "#FF4500"},
        }

        # Track current mode
        self.current_mode = "dark"

        # Create frames
        self.editor_frame = tk.Frame(root, bg="#2c2f38", padx=10, pady=10)
        self.editor_frame.pack(fill=tk.BOTH, expand=1)

        # Text editor
        self.text_editor = ScrolledText(self.editor_frame, wrap=tk.WORD, undo=True, height=20, font=("Arial", 12), bg="#2b2b2b", fg="white")
        self.text_editor.pack(fill=tk.BOTH, expand=1, padx=5, pady=5)
        self.text_editor.bind("<KeyRelease>", self.highlight_syntax)

        # Terminal frame
        self.terminal_frame = tk.Frame(root, bg="#2c2f38", height=150, padx=10, pady=10)
        self.terminal_frame.pack(fill=tk.BOTH, expand=1)

        # Output header
        self.output_header = tk.Label(self.terminal_frame, text="Output Box", fg="white", bg="#444444", font=("Arial", 14, "bold"))
        self.output_header.pack(fill=tk.X, pady=(5, 0))

        # Terminal output
        self.terminal_output = ScrolledText(self.terminal_frame, wrap=tk.WORD, height=8, state=tk.NORMAL, bg="#222222", fg="white", font=("Arial", 10))
        self.terminal_output.pack(fill=tk.BOTH, expand=1)

        # Input header
        self.input_header = tk.Label(self.terminal_frame, text="Input Box", fg="white", bg="#444444", font=("Arial", 14, "bold"))
        self.input_header.pack(fill=tk.X, pady=(10, 5))

        # Terminal input
        self.terminal_input = tk.Entry(self.terminal_frame, bg="#444444", fg="white", insertbackground="white", font=("Arial", 12))
        self.terminal_input.pack(fill=tk.X, padx=5, pady=5)
        self.terminal_input.bind("<Return>", self.send_input_to_script)

        # Menu
        self.menu = tk.Menu(root, bg="#333333", fg="white")
        self.root.config(menu=self.menu)

        # File Menu
        file_menu = tk.Menu(self.menu, tearoff=False, bg="#333333", fg="white")
        self.menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_application)

        # Run Menu
        run_menu = tk.Menu(self.menu, tearoff=False, bg="#333333", fg="white")
        self.menu.add_cascade(label="Run", menu=run_menu)
        run_menu.add_command(label="Run", command=self.run_babu_script, accelerator="F5")

        # View Menu
        view_menu = tk.Menu(self.menu, tearoff=False, bg="#333333", fg="white")
        self.menu.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Light Mode", command=self.set_light_mode)
        view_menu.add_command(label="Dark Mode", command=self.set_dark_mode)

        # Sound Menu
        sound_menu = tk.Menu(self.menu, tearoff=False, bg="#333333", fg="white")
        self.menu.add_cascade(label="Sound", menu=sound_menu)
        sound_menu.add_command(label="Mute", command=self.toggle_mute)

        # Bind shortcuts
        self.root.bind("<Control-n>", lambda event: self.new_file())
        self.root.bind("<Control-o>", lambda event: self.open_file())
        self.root.bind("<Control-s>", lambda event: self.save_file())
        self.root.bind("<F5>", lambda event: self.run_babu_script())

        # Process handling
        self.process = None
        self.waiting_for_input = False  # Flag to track if input is expected

    def play_sound(self, sound_name):
        """Play a sound if unmuted"""
        if not self.is_muted and sound_name in self.audio_files:
            try:
                sound_path = self.audio_files[sound_name]
                if os.path.exists(sound_path):
                    pygame.mixer.Sound(sound_path).play()
            except Exception as e:
                print(f"Error playing sound: {e}")


    def execute_script(self):
        if self.process and self.process.poll() is None:
            messagebox.showwarning("Script Running", "A script is already running.")
            return

        self.append_to_terminal("Running script...\n")
        self.play_sound('run')  # Play run sound when script starts
        
        self.process = subprocess.Popen(
            ["python", "main.py", self.current_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            text=True
        )
\
        # Read stdout and stderr
        threading.Thread(target=self.read_output, daemon=True).start()
        threading.Thread(target=self.read_error, daemon=True).start()

    def read_output(self):
        for line in iter(self.process.stdout.readline, ""):
            # Check for input prompts in the output
            if "input(" in line or "bolo shona" in line:
                self.waiting_for_input = True
                self.play_sound('input')
            self.append_to_terminal(line)

    def read_error(self):
        for line in iter(self.process.stderr.readline, ""):
            self.append_to_terminal(line, error=True)

    def send_input_to_script(self, event):
        user_input = self.terminal_input.get() + "\n"
        if self.process and self.process.stdin:
            self.process.stdin.write(user_input)
            self.process.stdin.flush()
        self.terminal_input.delete(0, tk.END)

    def toggle_mute(self):
        self.is_muted = not self.is_muted
        label = "Unmute" if self.is_muted else "Mute"
        sound_menu = self.menu.nametowidget(self.menu.entrycget("Sound", "menu"))
        sound_menu.entryconfigure(0, label=label)

    def highlight_syntax(self, event=None):
        text_content = self.text_editor.get("1.0", tk.END)
        for keyword, colors in self.keywords.items():
            self.text_editor.tag_remove(keyword, "1.0", tk.END)  # Clear old tags
            matches = re.finditer(r'\b' + re.escape(keyword) + r'\b', text_content)
            for match in matches:
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.text_editor.tag_add(keyword, start, end)
                self.text_editor.tag_config(keyword, foreground=colors[self.current_mode])


    def new_file(self):
        self.current_file = None
        self.text_editor.delete(1.0, tk.END)
        self.play_sound('new')

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Babu Files", "*.babu"), ("All Files", "*.*")])
        if file_path:
            self.current_file = file_path
            with open(file_path, "r") as file:
                self.text_editor.delete(1.0, tk.END)
                self.text_editor.insert(1.0, file.read())
            self.highlight_syntax()
            self.play_sound('open')

    def save_file(self):
        if self.current_file:
            with open(self.current_file, "w") as file:
                file.write(self.text_editor.get(1.0, tk.END).strip())
            self.play_sound('save')
        else:
            self.save_file_as()

    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".babu", filetypes=[("Babu Files", "*.babu"), ("All Files", "*.*")])
        if file_path:
            self.current_file = file_path
            with open(file_path, "w") as file:
                file.write(self.text_editor.get(1.0, tk.END).strip())
            self.play_sound('save_as')

    def run_babu_script(self):
        if not self.current_file:
            messagebox.showwarning("Save File", "Please save the file before running.")
            return

        #Save silently without playing sound
        with open(self.current_file, "w") as file:
            file.write(self.text_editor.get(1.0, tk.END).strip())
        
        # Play run sound and execute script
        self.play_sound('run')
        threading.Thread(target=self.execute_script).start()

    def execute_script(self):
        if self.process and self.process.poll() is None:
            messagebox.showwarning("Script Running", "A script is already running.")
            return

        self.append_to_terminal("Running script...\n")
        self.process = subprocess.Popen(
            ["python", "main.py", self.current_file],  # Pass the file path as an argument
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            text=True
        )

        # Read stdout and stderr
        threading.Thread(target=self.read_output, daemon=True).start()
        threading.Thread(target=self.read_error, daemon=True).start()

    def read_output(self):
        for line in iter(self.process.stdout.readline, ""):
            self.append_to_terminal(line)

    def read_error(self):
        for line in iter(self.process.stderr.readline, ""):
            self.append_to_terminal(line, error=True)


    def append_to_terminal(self, text, error=False):
        self.terminal_output.config(state=tk.NORMAL)
        if error:
            self.play_sound('error')
            self.terminal_output.insert(tk.END, text, "error")
            self.terminal_output.tag_config("error", foreground="red")
        else:
            self.terminal_output.insert(tk.END, text)
        self.terminal_output.see(tk.END)
        self.terminal_output.config(state=tk.DISABLED)

    def set_light_mode(self):
        self.current_mode = "light"
        self.text_editor.config(bg="white", fg="black", insertbackground="black", font=("Arial", 12))
        self.terminal_output.config(bg="white", fg="black", font=("Arial", 10))
        self.terminal_input.config(bg="white", fg="black", insertbackground="black", font=("Arial", 12))
        self.output_header.config(bg="#e0e0e0", fg="black")
        self.input_header.config(bg="#e0e0e0", fg="black")
        self.play_sound('light_mode')
        self.highlight_syntax()  # Reapply highlighting with the new mode

    def set_dark_mode(self):
        self.current_mode = "dark"
        self.text_editor.config(bg="black", fg="white", insertbackground="white", font=("Arial", 12))
        self.terminal_output.config(bg="black", fg="white", font=("Arial", 10))
        self.terminal_input.config(bg="black", fg="white", insertbackground="white", font=("Arial", 12))
        self.output_header.config(bg="#444444", fg="white")
        self.input_header.config(bg="#444444", fg="white")
        self.play_sound('dark_mode')
        self.highlight_syntax()  # Reapply highlighting with the new mode

    def add_window_controls(self):
        # Custom Minimize button
        minimize_button = tk.Button(self.root, text="–", command=self.root.iconify, bg="#3a3a3a", fg="white", font=("Arial", 10, "bold"), relief="flat")
        minimize_button.place(x=self.root.winfo_width() - 90, y=10, width=30, height=30)

        # Custom Maximize button
        maximize_button = tk.Button(self.root, text="□", command=self.toggle_maximize, bg="#3a3a3a", fg="white", font=("Arial", 10, "bold"), relief="flat")
        maximize_button.place(x=self.root.winfo_width() - 60, y=10, width=30, height=30)

        # Custom Close button
        close_button = tk.Button(self.root, text="×", command=self.root.quit, bg="#3a3a3a", fg="white", font=("Arial", 10, "bold"), relief="flat")
        close_button.place(x=self.root.winfo_width() - 30, y=10, width=30, height=30)

    def toggle_maximize(self):
        if self.root.state() == 'normal':
            self.root.state('zoomed')
        else:
            self.root.state('normal')

    def exit_application(self):
        self.play_sound('exit')
        self.root.after(1500, self.root.quit)  # Wait for sound to play before quitting

    def __del__(self):
        pygame.mixer.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = BabuIDE(root)
    root.mainloop()
