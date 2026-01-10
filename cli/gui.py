#!/usr/bin/env python3
"""
Splice3D GUI Launcher

Simple GUI for the post-processor using tkinter.
No external dependencies required.

Usage: python gui.py
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import sys
import os
from pathlib import Path


class Splice3DGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Splice3D Post-Processor")
        self.root.geometry("700x500")
        
        # Variables
        self.input_file = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.color_a = tk.StringVar(value="white")
        self.color_b = tk.StringVar(value="black")
        self.min_segment = tk.StringVar(value="5.0")
        self.transition = tk.StringVar(value="10.0")
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main frame
        main = ttk.Frame(self.root, padding="10")
        main.pack(fill=tk.BOTH, expand=True)
        
        # Input file
        ttk.Label(main, text="Input G-code:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main, textvariable=self.input_file, width=50).grid(row=0, column=1, pady=5)
        ttk.Button(main, text="Browse...", command=self.browse_input).grid(row=0, column=2, padx=5)
        
        # Output directory
        ttk.Label(main, text="Output Directory:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main, textvariable=self.output_dir, width=50).grid(row=1, column=1, pady=5)
        ttk.Button(main, text="Browse...", command=self.browse_output).grid(row=1, column=2, padx=5)
        
        # Colors frame
        colors_frame = ttk.LabelFrame(main, text="Colors", padding="5")
        colors_frame.grid(row=2, column=0, columnspan=3, sticky=tk.EW, pady=10)
        
        ttk.Label(colors_frame, text="Color A (T0):").grid(row=0, column=0, padx=5)
        ttk.Entry(colors_frame, textvariable=self.color_a, width=15).grid(row=0, column=1, padx=5)
        
        ttk.Label(colors_frame, text="Color B (T1):").grid(row=0, column=2, padx=5)
        ttk.Entry(colors_frame, textvariable=self.color_b, width=15).grid(row=0, column=3, padx=5)
        
        # Settings frame
        settings_frame = ttk.LabelFrame(main, text="Settings", padding="5")
        settings_frame.grid(row=3, column=0, columnspan=3, sticky=tk.EW, pady=10)
        
        ttk.Label(settings_frame, text="Min Segment (mm):").grid(row=0, column=0, padx=5)
        ttk.Entry(settings_frame, textvariable=self.min_segment, width=10).grid(row=0, column=1, padx=5)
        
        ttk.Label(settings_frame, text="Transition (mm):").grid(row=0, column=2, padx=5)
        ttk.Entry(settings_frame, textvariable=self.transition, width=10).grid(row=0, column=3, padx=5)
        
        # Process button
        ttk.Button(main, text="Process G-code", command=self.process).grid(row=4, column=0, columnspan=3, pady=20)
        
        # Output log
        ttk.Label(main, text="Output:").grid(row=5, column=0, sticky=tk.W)
        self.log = scrolledtext.ScrolledText(main, height=12, width=80)
        self.log.grid(row=6, column=0, columnspan=3, pady=5)
    
    def browse_input(self):
        filename = filedialog.askopenfilename(
            title="Select G-code file",
            filetypes=[("G-code files", "*.gcode"), ("All files", "*.*")]
        )
        if filename:
            self.input_file.set(filename)
            # Set default output dir to same directory
            if not self.output_dir.get():
                self.output_dir.set(str(Path(filename).parent))
    
    def browse_output(self):
        directory = filedialog.askdirectory(title="Select output directory")
        if directory:
            self.output_dir.set(directory)
    
    def log_message(self, msg):
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)
        self.root.update()
    
    def process(self):
        # Validate input
        if not self.input_file.get():
            messagebox.showerror("Error", "Please select an input file")
            return
        
        if not Path(self.input_file.get()).exists():
            messagebox.showerror("Error", "Input file does not exist")
            return
        
        self.log.delete(1.0, tk.END)
        self.log_message("Processing...")
        
        # Build command
        script_dir = Path(__file__).parent.parent / "postprocessor"
        script = script_dir / "splice3d_postprocessor.py"
        
        cmd = [
            sys.executable, str(script),
            self.input_file.get(),
            "--colors", self.color_a.get(), self.color_b.get(),
            "--min-segment", self.min_segment.get(),
            "--transition", self.transition.get(),
            "-v"
        ]
        
        if self.output_dir.get():
            cmd.extend(["--output-dir", self.output_dir.get()])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(script_dir)
            )
            
            self.log_message(result.stdout)
            if result.stderr:
                self.log_message("STDERR: " + result.stderr)
            
            if result.returncode == 0:
                self.log_message("\n✓ Processing complete!")
                messagebox.showinfo("Success", "G-code processed successfully!")
            else:
                self.log_message(f"\n✗ Error (code {result.returncode})")
                
        except Exception as e:
            self.log_message(f"Error: {e}")
            messagebox.showerror("Error", str(e))


def main():
    root = tk.Tk()
    app = Splice3DGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
