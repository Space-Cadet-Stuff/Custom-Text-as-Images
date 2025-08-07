#!/usr/bin/env python3
"""
Font Image Maker - A desktop application for creating customizable text images
"""

import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox
import os
import json
import shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
import platform
import tempfile
import math
import re
import subprocess
import numpy as np

# Optional imports - may not be available on all systems
try:
    import win32clipboard
except ImportError:
    win32clipboard = None

class FontImageMaker:
    def __init__(self, root):
        self.root = root
        self.root.title("TextLab")
        
        # Set icon for window and taskbar
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")
            if os.path.exists(icon_path):
                # Set icon for both window and taskbar
                self.root.iconbitmap(icon_path)
                # Alternative method for taskbar icon (Windows-specific enhancement)
                self.root.wm_iconbitmap(icon_path)
        except Exception as e:
            # If icon loading fails, continue without icon
            print(f"Warning: Could not load icon: {e}")
        
        # Set responsive window size (80% of screen size, min 1000x700)
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = max(1000, int(screen_width * 0.8))
        window_height = max(700, int(screen_height * 0.8))
        
        # Center the window on screen
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(1000, 700)  # Set minimum window size
        
        # Initialize variables
        self.setup_variables()
        
        # Create directories
        self.create_directories()
        
        # Setup GUI
        self.setup_gui()
        
        # Bind window resize to adjust layout
        self.root.bind('<Configure>', self.on_window_resize)
        
        # Update color button appearances
        self.update_color_buttons()
        
        # Load fonts from configured directories
        self.load_fonts()
        
        # Update directory info display
        self.update_directory_info()
        
        # Load available presets
        self.load_preset_list()
        
        # Initialize preview
        self.update_preview()
        
        # Final layout adjustment after everything is loaded
        self.root.after(200, self.adjust_preview_panel)
    
    def setup_variables(self):
        """Initialize all tkinter variables"""
        # Text variables
        self.text_var = tk.StringVar(value="Sample Text")
        self.font_size_var = tk.IntVar(value=48)
        
        # Text colors
        self.text_color_var = tk.StringVar(value="#000000")
        self.text_color2_var = tk.StringVar(value="#FFFFFF")
        self.text_outline_color_var = tk.StringVar(value="#FFFFFF")
        self.text_glow_color_var = tk.StringVar(value="#0000FF")
        
        # Text effects
        self.glow_intensity_var = tk.IntVar(value=19)  # 19% = 75 in old scale (75/4 = 18.75 ≈ 19)
        self.glow_radius_var = tk.IntVar(value=5)
        self.outline_thickness_var = tk.IntVar(value=2)
        self.glow_enabled_var = tk.BooleanVar(value=True)
        
        # Text gradient
        self.text_gradient_var = tk.StringVar(value="None")
        self.text_gradient_angle_var = tk.IntVar(value=0)
        self.text_gradient_size_var = tk.IntVar(value=100)
        
        # Background variables
        self.bg_opacity_var = tk.IntVar(value=100)
        self.bg_color_var = tk.StringVar(value="#FFFFFF")
        self.bg_color2_var = tk.StringVar(value="#000000")
        self.bg_gradient_var = tk.StringVar(value="None")
        self.bg_gradient_angle_var = tk.IntVar(value=0)
        self.bg_gradient_size_var = tk.IntVar(value=100)
        
        # Image size
        self.image_width_var = tk.IntVar(value=800)
        self.image_height_var = tk.IntVar(value=400)
        
        # Margins/Padding
        self.margin_left_var = tk.IntVar(value=10)
        self.margin_right_var = tk.IntVar(value=10)
        self.margin_top_var = tk.IntVar(value=10)
        self.margin_bottom_var = tk.IntVar(value=10)
        
        # Alignment
        self.alignment_var = tk.StringVar(value="center")
        
        # Font
        self.font_var = tk.StringVar()
        
        # Preset selection
        self.preset_var = tk.StringVar()
        
        # Available fonts list
        self.available_fonts = []
        self.font_paths = {}
        
        # Font directories
        self.font_directories = []  # List of directories to load fonts from
        
        # Font cache for performance optimization
        self._font_cache = {}
        self._font_cache_max_size = 10  # Maximum number of cached fonts
        
        # Color conversion cache for performance
        self._color_cache = {}
        self._color_cache_max_size = 50
        
        # Current preview image
        self.preview_image = None
        
        # Debouncing for preview updates to improve performance
        self._preview_update_id = None
        self._preview_update_delay = 150  # milliseconds
    
    def create_directories(self):
        """Create necessary directories"""
        os.makedirs("fonts", exist_ok=True)
        os.makedirs("presets", exist_ok=True)
        
        # Load font directories from config file
        self.load_font_directories_config()
        
        # If no directories are configured, use the default fonts directory
        if not self.font_directories:
            default_fonts_dir = os.path.abspath("fonts")
            self.font_directories = [default_fonts_dir]
            self.save_font_directories_config()
    
    def setup_gui(self):
        """Setup the main GUI"""
        # Create main frames
        self.create_main_frames()
        
        # Create control panels
        self.create_text_controls()
        self.create_background_controls()
        self.create_general_controls()
        self.create_preview_panel()
        self.create_action_buttons()
        
        # Bind sidebar scrolling to all control widgets
        self.root.after(200, lambda: self.bind_sidebar_scroll(self.scrollable_frame))
    
    def create_main_frames(self):
        """Create main layout frames with fixed sidebar width"""
        SIDEBAR_WIDTH = 430
        
        # Left panel for controls with scrollbar
        self.left_frame = ttk.Frame(self.root, width=SIDEBAR_WIDTH)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=3, pady=3)
        self.left_frame.pack_propagate(False)
        
        # Create canvas and scrollbar for left frame
        canvas_width = SIDEBAR_WIDTH - 20
        self.canvas = tk.Canvas(self.left_frame, width=canvas_width)
        self.scrollbar = ttk.Scrollbar(self.left_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas for sidebar scrolling
        def _on_sidebar_mousewheel(event):
            try:
                self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except tk.TclError:
                pass  # Ignore scroll errors when no content
        
        # Bind mousewheel events to multiple widgets in the sidebar for better coverage
        self.canvas.bind("<MouseWheel>", _on_sidebar_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", _on_sidebar_mousewheel)
        self.left_frame.bind("<MouseWheel>", _on_sidebar_mousewheel)
        
        # Also bind to Button-4 and Button-5 for Linux compatibility
        def _on_sidebar_button4(event):
            try:
                self.canvas.yview_scroll(-1, "units")
            except tk.TclError:
                pass
                
        def _on_sidebar_button5(event):
            try:
                self.canvas.yview_scroll(1, "units")
            except tk.TclError:
                pass
        
        self.canvas.bind("<Button-4>", _on_sidebar_button4)
        self.canvas.bind("<Button-5>", _on_sidebar_button5)
        self.scrollable_frame.bind("<Button-4>", _on_sidebar_button4)
        self.scrollable_frame.bind("<Button-5>", _on_sidebar_button5)
        
        # Bind mouse enter events to ensure focus for scrolling
        def _on_sidebar_enter(event):
            # Focus the canvas for consistent scrolling behavior
            self.canvas.focus_set()
        
        self.canvas.bind("<Enter>", _on_sidebar_enter)
        self.scrollable_frame.bind("<Enter>", _on_sidebar_enter)
        self.left_frame.bind("<Enter>", _on_sidebar_enter)
        
        # Make sidebar canvas focusable for keyboard navigation
        self.canvas.configure(takefocus=True)
        
        # Bind keyboard scrolling for sidebar
        def _on_sidebar_key_press(event):
            if event.keysym == "Up":
                self.canvas.yview_scroll(-1, "units")
            elif event.keysym == "Down":
                self.canvas.yview_scroll(1, "units")
            elif event.keysym == "Prior":  # Page Up
                self.canvas.yview_scroll(-10, "units")
            elif event.keysym == "Next":   # Page Down
                self.canvas.yview_scroll(10, "units")
        
        self.canvas.bind("<Key>", _on_sidebar_key_press)
        
        # Focus sidebar canvas when clicked
        def _on_sidebar_click(event):
            self.canvas.focus_set()
        
        self.canvas.bind("<Button-1>", _on_sidebar_click)
        
        # Store the sidebar scroll function for child widgets to use
        self._sidebar_scroll_function = _on_sidebar_mousewheel
        
        # Right panel for preview - this will take remaining space
        self.right_frame = ttk.Frame(self.root)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        # Initial layout adjustment after frames are created
        self.root.after(100, self.adjust_preview_panel)
    
    def bind_sidebar_scroll(self, widget):
        """Bind mouse wheel scrolling to a widget so it scrolls the sidebar"""
        if hasattr(self, '_sidebar_scroll_function'):
            widget.bind("<MouseWheel>", self._sidebar_scroll_function)
            widget.bind("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
            widget.bind("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))
            
            # Recursively bind to all child widgets
            for child in widget.winfo_children():
                self.bind_sidebar_scroll(child)
    
    def on_window_resize(self, event):
        """Handle window resize events to adjust preview panel"""
        # Only handle main window resize events, not child widget events
        if event.widget == self.root:
            self.adjust_preview_panel()
    
    def adjust_preview_panel(self):
        """Adjust preview panel size based on available space"""
        # Get current window dimensions
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        
        # Use fixed sidebar width
        sidebar_width = 415
        
        # Calculate available space for preview
        # Account for: sidebar width + padding between panels + outer padding
        total_padding = 12
        available_width = window_width - sidebar_width - total_padding
        
        # Ensure minimum preview width
        min_preview_width = 400
        if available_width < min_preview_width:
            available_width = min_preview_width
        
        # Update right frame to use calculated width
        if hasattr(self, 'right_frame'):
            # Force update the right frame to fill remaining space efficiently
            self.right_frame.pack_configure(fill=tk.BOTH, expand=True)
            
            # Update preview canvas size hints if it exists
            if hasattr(self, 'preview_canvas'):
                # Set a reasonable default size for the canvas based on available space
                canvas_width = max(400, available_width - 30)  # Account for scrollbars and padding
                canvas_height = max(300, window_height - 150)  # Account for title bar and padding
                
                # Don't force exact size, but provide size hints
                self.preview_canvas.configure(width=canvas_width, height=canvas_height)
    
    def create_text_controls(self):
        """Create text customization controls"""
        text_frame = ttk.LabelFrame(self.scrollable_frame, text="Text Settings", padding=10)
        text_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Text input
        ttk.Label(text_frame, text="Text:").grid(row=0, column=0, sticky=tk.W, pady=2)
        text_entry = ttk.Entry(text_frame, textvariable=self.text_var, width=30)
        text_entry.grid(row=0, column=1, columnspan=2, sticky=tk.EW, pady=2)
        text_entry.bind('<KeyRelease>', lambda e: self.update_preview_debounced())
        
        # Preset selector
        ttk.Label(text_frame, text="Preset:").grid(row=1, column=0, sticky=tk.W, pady=2)
        
        preset_frame = ttk.Frame(text_frame)
        preset_frame.grid(row=1, column=1, columnspan=2, sticky=tk.EW, pady=2)
        
        self.preset_combo = ttk.Combobox(preset_frame, textvariable=self.preset_var, width=18, state="readonly")
        self.preset_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.preset_combo.bind('<<ComboboxSelected>>', self.load_selected_preset)
        
        # Save preset button
        save_preset_btn = ttk.Button(preset_frame, text="Save Preset", command=self.save_preset)
        save_preset_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Font size slider
        ttk.Label(text_frame, text="Size:").grid(row=2, column=0, sticky=tk.W, pady=2)
        size_frame = ttk.Frame(text_frame)
        size_frame.grid(row=2, column=1, columnspan=2, sticky=tk.EW, pady=2)
        
        size_scale = ttk.Scale(size_frame, from_=8, to=200, orient=tk.HORIZONTAL,
                              variable=self.font_size_var, command=lambda v: self.update_preview_debounced())
        size_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Add unit label
        ttk.Label(size_frame, text="pt").pack(side=tk.RIGHT, padx=(1, 5))
        
        self.size_entry = ttk.Entry(size_frame, textvariable=self.font_size_var, width=6)
        self.size_entry.pack(side=tk.RIGHT, padx=(5, 0))
        self.size_entry.bind('<Return>', lambda e: self.update_preview())
        self.size_entry.bind('<FocusOut>', lambda e: self.update_preview())
        
        # Font selection
        ttk.Label(text_frame, text="Font:").grid(row=3, column=0, sticky=tk.W, pady=2)
        
        font_frame = ttk.Frame(text_frame)
        font_frame.grid(row=3, column=1, columnspan=2, sticky=tk.EW, pady=2)
        
        # Font display label and select button
        self.font_display_label = ttk.Label(font_frame, text="Arial", relief="sunken", width=20)
        self.font_display_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        select_font_btn = ttk.Button(font_frame, text="Select Font", command=self.open_font_selector)
        select_font_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Upload font button
        upload_font_btn = ttk.Button(font_frame, text="Upload Font", command=self.upload_font)
        upload_font_btn.pack(side=tk.RIGHT)
        
        # Font directories management
        ttk.Label(text_frame, text="Font Directories:").grid(row=4, column=0, sticky=tk.W, pady=2)
        
        directories_frame = ttk.Frame(text_frame)
        directories_frame.grid(row=4, column=1, columnspan=2, sticky=tk.EW, pady=2)
        
        # Show current number of directories
        self.directories_info_label = ttk.Label(directories_frame, text="0 directories")
        self.directories_info_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        manage_dirs_btn = ttk.Button(directories_frame, text="Manage Directories", command=self.manage_font_directories)
        manage_dirs_btn.pack(side=tk.RIGHT)
        
        # Add blank line after Font Directories
        ttk.Label(text_frame, text="").grid(row=4, column=3, pady=5)
        
        # Text colors
        ttk.Label(text_frame, text="Primary Color:").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.text_color_btn = tk.Button(text_frame, width=10, command=lambda: self.choose_color(self.text_color_var, self.text_color_btn))
        self.text_color_btn.grid(row=5, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(text_frame, text="Secondary Color\n(Optional):").grid(row=6, column=0, sticky=tk.W, pady=2)
        self.text_color2_btn = tk.Button(text_frame, width=10, command=lambda: self.choose_color(self.text_color2_var, self.text_color2_btn))
        self.text_color2_btn.grid(row=6, column=1, sticky=tk.W, pady=2)
        
        # Text gradient
        ttk.Label(text_frame, text="Gradient Type:").grid(row=7, column=0, sticky=tk.W, pady=2)
        gradient_combo = ttk.Combobox(text_frame, textvariable=self.text_gradient_var, 
                                    values=["None", "Linear", "Radial", "Circular"], state="readonly", width=15)
        gradient_combo.grid(row=7, column=1, sticky=tk.W, pady=2)
        gradient_combo.bind('<<ComboboxSelected>>', lambda e: self.update_preview())
        
        # Gradient angle
        ttk.Label(text_frame, text="Gradient Angle:").grid(row=8, column=0, sticky=tk.W, pady=2)
        gradient_angle_frame = ttk.Frame(text_frame)
        gradient_angle_frame.grid(row=8, column=1, columnspan=2, sticky=tk.EW, pady=2)
        
        angle_scale = ttk.Scale(gradient_angle_frame, from_=0, to=360, orient=tk.HORIZONTAL, 
                              variable=self.text_gradient_angle_var, command=lambda v: self.update_preview_debounced())
        angle_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(gradient_angle_frame, text="°").pack(side=tk.RIGHT, padx=(1, 5))
        
        self.gradient_angle_entry = ttk.Entry(gradient_angle_frame, textvariable=self.text_gradient_angle_var, width=6)
        self.gradient_angle_entry.pack(side=tk.RIGHT, padx=(5, 0))
        self.gradient_angle_entry.bind('<Return>', lambda e: self.update_preview())
        self.gradient_angle_entry.bind('<FocusOut>', lambda e: self.update_preview())
        
        # Gradient size
        ttk.Label(text_frame, text="Gradient Width:").grid(row=9, column=0, sticky=tk.W, pady=2)
        gradient_size_frame = ttk.Frame(text_frame)
        gradient_size_frame.grid(row=9, column=1, columnspan=2, sticky=tk.EW, pady=2)
        
        gradient_size_scale = ttk.Scale(gradient_size_frame, from_=0, to=100, orient=tk.HORIZONTAL, 
                                      variable=self.text_gradient_size_var, command=lambda v: self.update_preview_debounced())
        gradient_size_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(gradient_size_frame, text="%").pack(side=tk.RIGHT, padx=(1, 5))
        
        self.gradient_size_entry = ttk.Entry(gradient_size_frame, textvariable=self.text_gradient_size_var, width=6)
        self.gradient_size_entry.pack(side=tk.RIGHT, padx=(5, 0))
        self.gradient_size_entry.bind('<Return>', lambda e: self.update_preview())
        self.gradient_size_entry.bind('<FocusOut>', lambda e: self.update_preview())
        
        # Add blank line after Gradient Width
        ttk.Label(text_frame, text="").grid(row=9, column=3, pady=5)
        
        # Text outline
        ttk.Label(text_frame, text="Outline Color:").grid(row=10, column=0, sticky=tk.W, pady=2)
        self.outline_color_btn = tk.Button(text_frame, width=10, command=lambda: self.choose_color(self.text_outline_color_var, self.outline_color_btn))
        self.outline_color_btn.grid(row=10, column=1, sticky=tk.W, pady=2)
        
        # Outline thickness
        ttk.Label(text_frame, text="Outline\nThickness:").grid(row=11, column=0, sticky=tk.W, pady=2)
        outline_frame = ttk.Frame(text_frame)
        outline_frame.grid(row=11, column=1, columnspan=2, sticky=tk.EW, pady=2)
        
        outline_scale = ttk.Scale(outline_frame, from_=0, to=10, orient=tk.HORIZONTAL,
                                variable=self.outline_thickness_var, command=lambda v: self.update_preview_debounced())
        outline_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(outline_frame, text="px").pack(side=tk.RIGHT, padx=(1, 5))
        
        self.outline_entry = ttk.Entry(outline_frame, textvariable=self.outline_thickness_var, width=6)
        self.outline_entry.pack(side=tk.RIGHT, padx=(5, 0))
        self.outline_entry.bind('<Return>', lambda e: self.update_preview())
        self.outline_entry.bind('<FocusOut>', lambda e: self.update_preview())
        
        # Add blank line after Outline Thickness
        ttk.Label(text_frame, text="").grid(row=11, column=3, pady=5)
        
        # Text glow
        ttk.Label(text_frame, text="Glow Color:").grid(row=12, column=0, sticky=tk.W, pady=2)
        self.glow_color_btn = tk.Button(text_frame, width=10, command=lambda: self.choose_color(self.text_glow_color_var, self.glow_color_btn))
        self.glow_color_btn.grid(row=12, column=1, sticky=tk.W, pady=2)
        
        # Glow enable checkbox
        self.glow_enabled_cb = ttk.Checkbutton(text_frame, text="Enable Glow", variable=self.glow_enabled_var, command=self.update_preview)
        self.glow_enabled_cb.grid(row=12, column=2, sticky=tk.W, pady=2)
        
        # Glow intensity
        ttk.Label(text_frame, text="Glow Intensity:").grid(row=13, column=0, sticky=tk.W, pady=2)
        glow_intensity_frame = ttk.Frame(text_frame)
        glow_intensity_frame.grid(row=13, column=1, columnspan=2, sticky=tk.EW, pady=2)
        
        glow_intensity_scale = ttk.Scale(glow_intensity_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                       variable=self.glow_intensity_var, command=lambda v: self.update_preview_debounced())
        glow_intensity_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(glow_intensity_frame, text="%").pack(side=tk.RIGHT, padx=(1, 5))
        
        self.glow_intensity_entry = ttk.Entry(glow_intensity_frame, textvariable=self.glow_intensity_var, width=6)
        self.glow_intensity_entry.pack(side=tk.RIGHT, padx=(5, 0))
        self.glow_intensity_entry.bind('<Return>', lambda e: self.update_preview())
        self.glow_intensity_entry.bind('<FocusOut>', lambda e: self.update_preview())
        
        # Glow radius
        ttk.Label(text_frame, text="Glow Radius:").grid(row=14, column=0, sticky=tk.W, pady=2)
        glow_radius_frame = ttk.Frame(text_frame)
        glow_radius_frame.grid(row=14, column=1, columnspan=2, sticky=tk.EW, pady=2)
        
        glow_radius_scale = ttk.Scale(glow_radius_frame, from_=0, to=20, orient=tk.HORIZONTAL,
                                    variable=self.glow_radius_var, command=lambda v: self.update_preview_debounced())
        glow_radius_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(glow_radius_frame, text="px").pack(side=tk.RIGHT, padx=(1, 5))
        
        self.glow_radius_entry = ttk.Entry(glow_radius_frame, textvariable=self.glow_radius_var, width=6)
        self.glow_radius_entry.pack(side=tk.RIGHT, padx=(5, 0))
        self.glow_radius_entry.bind('<Return>', lambda e: self.update_preview())
        self.glow_radius_entry.bind('<FocusOut>', lambda e: self.update_preview())
        
        # Configure grid weights
        text_frame.columnconfigure(1, weight=1)
    
    def create_background_controls(self):
        """Create background customization controls"""
        bg_frame = ttk.LabelFrame(self.scrollable_frame, text="Background Settings", padding=10)
        bg_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Opacity
        ttk.Label(bg_frame, text="Opacity:").grid(row=0, column=0, sticky=tk.W, pady=2)
        opacity_frame = ttk.Frame(bg_frame)
        opacity_frame.grid(row=0, column=1, columnspan=2, sticky=tk.EW, pady=2)
        
        opacity_scale = ttk.Scale(opacity_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                variable=self.bg_opacity_var, command=lambda v: self.update_preview())
        opacity_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(opacity_frame, text="%").pack(side=tk.RIGHT, padx=(1, 5))
        
        self.opacity_entry = ttk.Entry(opacity_frame, textvariable=self.bg_opacity_var, width=6)
        self.opacity_entry.pack(side=tk.RIGHT, padx=(5, 0))
        self.opacity_entry.bind('<Return>', lambda e: self.update_preview())
        self.opacity_entry.bind('<FocusOut>', lambda e: self.update_preview())
        
        # Add blank line after Opacity
        ttk.Label(bg_frame, text="").grid(row=0, column=3, pady=5)
        
        # Background colors
        ttk.Label(bg_frame, text="Primary Color:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.bg_color_btn = tk.Button(bg_frame, width=10, command=lambda: self.choose_color(self.bg_color_var, self.bg_color_btn))
        self.bg_color_btn.grid(row=1, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(bg_frame, text="Secondary Color\n(Optional):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.bg_color2_btn = tk.Button(bg_frame, width=10, command=lambda: self.choose_color(self.bg_color2_var, self.bg_color2_btn))
        self.bg_color2_btn.grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # Background gradient
        ttk.Label(bg_frame, text="Gradient Type:").grid(row=3, column=0, sticky=tk.W, pady=2)
        bg_gradient_combo = ttk.Combobox(bg_frame, textvariable=self.bg_gradient_var,
                                       values=["None", "Linear", "Radial", "Circular"], state="readonly", width=15)
        bg_gradient_combo.grid(row=3, column=1, sticky=tk.W, pady=2)
        bg_gradient_combo.bind('<<ComboboxSelected>>', lambda e: self.update_preview())
        
        # Background gradient angle
        ttk.Label(bg_frame, text="Gradient Angle:").grid(row=4, column=0, sticky=tk.W, pady=2)
        bg_angle_frame = ttk.Frame(bg_frame)
        bg_angle_frame.grid(row=4, column=1, columnspan=2, sticky=tk.EW, pady=2)
        
        bg_angle_scale = ttk.Scale(bg_angle_frame, from_=0, to=360, orient=tk.HORIZONTAL,
                                 variable=self.bg_gradient_angle_var, command=lambda v: self.update_preview())
        bg_angle_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(bg_angle_frame, text="°").pack(side=tk.RIGHT, padx=(1, 5))
        
        self.bg_angle_entry = ttk.Entry(bg_angle_frame, textvariable=self.bg_gradient_angle_var, width=6)
        self.bg_angle_entry.pack(side=tk.RIGHT, padx=(5, 0))
        self.bg_angle_entry.bind('<Return>', lambda e: self.update_preview())
        self.bg_angle_entry.bind('<FocusOut>', lambda e: self.update_preview())
        
        # Background gradient size
        ttk.Label(bg_frame, text="Gradient Width:").grid(row=5, column=0, sticky=tk.W, pady=2)
        bg_gradient_size_frame = ttk.Frame(bg_frame)
        bg_gradient_size_frame.grid(row=5, column=1, columnspan=2, sticky=tk.EW, pady=2)
        
        bg_gradient_size_scale = ttk.Scale(bg_gradient_size_frame, from_=0, to=100, orient=tk.HORIZONTAL, 
                                         variable=self.bg_gradient_size_var, command=lambda v: self.update_preview())
        bg_gradient_size_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(bg_gradient_size_frame, text="%").pack(side=tk.RIGHT, padx=(1, 5))
        
        self.bg_gradient_size_entry = ttk.Entry(bg_gradient_size_frame, textvariable=self.bg_gradient_size_var, width=6)
        self.bg_gradient_size_entry.pack(side=tk.RIGHT, padx=(5, 0))
        self.bg_gradient_size_entry.bind('<Return>', lambda e: self.update_preview())
        self.bg_gradient_size_entry.bind('<FocusOut>', lambda e: self.update_preview())
        
        # Configure grid weights
        bg_frame.columnconfigure(1, weight=1)
    
    def safe_get_numeric(self, var, default_value, min_val=None, max_val=None):
        """Safely get numeric value from tkinter variable with fallback"""
        try:
            value = var.get()
            if min_val is not None:
                value = max(min_val, value)
            if max_val is not None:
                value = min(max_val, value)
            return value
        except (ValueError, tk.TclError):
            return default_value
    
    def create_general_controls(self):
        """Create general settings controls"""
        general_frame = ttk.LabelFrame(self.scrollable_frame, text="General Settings", padding=10)
        general_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Image size
        ttk.Label(general_frame, text="Image Size:").grid(row=0, column=0, sticky=tk.W, pady=2)
        
        size_frame = ttk.Frame(general_frame)
        size_frame.grid(row=0, column=1, columnspan=2, sticky=tk.EW, pady=2)
        
        width_spin = ttk.Spinbox(size_frame, from_=100, to=5000, textvariable=self.image_width_var, width=8)
        width_spin.pack(side=tk.LEFT)
        width_spin.bind('<KeyRelease>', lambda e: self.update_preview())
        width_spin.bind('<ButtonRelease-1>', lambda e: self.update_preview())
        
        ttk.Label(size_frame, text=" x ").pack(side=tk.LEFT)
        
        height_spin = ttk.Spinbox(size_frame, from_=100, to=5000, textvariable=self.image_height_var, width=8)
        height_spin.pack(side=tk.LEFT)
        height_spin.bind('<KeyRelease>', lambda e: self.update_preview())
        height_spin.bind('<ButtonRelease-1>', lambda e: self.update_preview())
        
        ttk.Label(size_frame, text=" px").pack(side=tk.LEFT)
        
        # Margins/Padding
        ttk.Label(general_frame, text="Margins:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        # Left margin
        ttk.Label(general_frame, text="Left:").grid(row=1, column=1, sticky=tk.W, pady=2, padx=(0, 5))
        left_margin_frame = ttk.Frame(general_frame)
        left_margin_frame.grid(row=1, column=2, sticky=tk.EW, pady=2)
        
        left_margin_scale = ttk.Scale(left_margin_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                    variable=self.margin_left_var, command=lambda v: self.update_preview())
        left_margin_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(left_margin_frame, text="px").pack(side=tk.RIGHT, padx=(1, 5))
        
        self.left_margin_entry = ttk.Entry(left_margin_frame, textvariable=self.margin_left_var, width=6)
        self.left_margin_entry.pack(side=tk.RIGHT, padx=(5, 0))
        self.left_margin_entry.bind('<Return>', lambda e: self.update_preview())
        self.left_margin_entry.bind('<FocusOut>', lambda e: self.update_preview())
        
        # Right margin
        ttk.Label(general_frame, text="Right:").grid(row=2, column=1, sticky=tk.W, pady=2, padx=(0, 5))
        right_margin_frame = ttk.Frame(general_frame)
        right_margin_frame.grid(row=2, column=2, sticky=tk.EW, pady=2)
        
        right_margin_scale = ttk.Scale(right_margin_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                     variable=self.margin_right_var, command=lambda v: self.update_preview())
        right_margin_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(right_margin_frame, text="px").pack(side=tk.RIGHT, padx=(1, 5))
        
        self.right_margin_entry = ttk.Entry(right_margin_frame, textvariable=self.margin_right_var, width=6)
        self.right_margin_entry.pack(side=tk.RIGHT, padx=(5, 0))
        self.right_margin_entry.bind('<Return>', lambda e: self.update_preview())
        self.right_margin_entry.bind('<FocusOut>', lambda e: self.update_preview())
        
        # Top margin
        ttk.Label(general_frame, text="Top:").grid(row=3, column=1, sticky=tk.W, pady=2, padx=(0, 5))
        top_margin_frame = ttk.Frame(general_frame)
        top_margin_frame.grid(row=3, column=2, sticky=tk.EW, pady=2)
        
        top_margin_scale = ttk.Scale(top_margin_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                   variable=self.margin_top_var, command=lambda v: self.update_preview())
        top_margin_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(top_margin_frame, text="px").pack(side=tk.RIGHT, padx=(1, 5))
        
        self.top_margin_entry = ttk.Entry(top_margin_frame, textvariable=self.margin_top_var, width=6)
        self.top_margin_entry.pack(side=tk.RIGHT, padx=(5, 0))
        self.top_margin_entry.bind('<Return>', lambda e: self.update_preview())
        self.top_margin_entry.bind('<FocusOut>', lambda e: self.update_preview())
        
        # Bottom margin
        ttk.Label(general_frame, text="Bottom:").grid(row=4, column=1, sticky=tk.W, pady=2, padx=(0, 5))
        bottom_margin_frame = ttk.Frame(general_frame)
        bottom_margin_frame.grid(row=4, column=2, sticky=tk.EW, pady=2)
        
        bottom_margin_scale = ttk.Scale(bottom_margin_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                      variable=self.margin_bottom_var, command=lambda v: self.update_preview())
        bottom_margin_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(bottom_margin_frame, text="px").pack(side=tk.RIGHT, padx=(1, 5))
        
        self.bottom_margin_entry = ttk.Entry(bottom_margin_frame, textvariable=self.margin_bottom_var, width=6)
        self.bottom_margin_entry.pack(side=tk.RIGHT, padx=(5, 0))
        self.bottom_margin_entry.bind('<Return>', lambda e: self.update_preview())
        self.bottom_margin_entry.bind('<FocusOut>', lambda e: self.update_preview())
        
        # Text alignment
        ttk.Label(general_frame, text="Text\nAlignment:").grid(row=5, column=0, sticky=tk.NW, pady=5)
        
        alignment_frame = ttk.Frame(general_frame)
        alignment_frame.grid(row=5, column=1, columnspan=2, sticky=tk.EW, pady=5)
        
        # Create 3x3 grid of alignment buttons
        alignments = [
            ["nw", "n", "ne"],
            ["w", "center", "e"],
            ["sw", "s", "se"]
        ]
        
        alignment_names = [
            ["Top-Left", "Top", "Top-Right"],
            ["Left", "Center", "Right"],
            ["Bottom-Left", "Bottom", "Bottom-Right"]
        ]
        
        for i, row in enumerate(alignments):
            for j, align in enumerate(row):
                btn = ttk.Radiobutton(alignment_frame, text=alignment_names[i][j], 
                                    variable=self.alignment_var, value=align,
                                    command=self.update_preview)
                btn.grid(row=i, column=j, padx=2, pady=2, sticky=tk.W)
        
        # Configure grid weights
        general_frame.columnconfigure(1, weight=1)
    
    def create_preview_panel(self):
        """Create the preview panel"""
        preview_frame = ttk.LabelFrame(self.right_frame, text="Preview", padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a frame to hold canvas and scrollbars
        canvas_frame = ttk.Frame(preview_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create canvas for preview with dynamic sizing
        self.preview_canvas = tk.Canvas(canvas_frame, bg="white")
        
        # Scrollbars for canvas
        h_scroll = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.preview_canvas.xview)
        v_scroll = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.preview_canvas.yview)
        
        # Configure canvas scrolling
        self.preview_canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
        
        # Pack scrollbars and canvas
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.preview_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind mousewheel to canvas for scrolling
        def _on_mousewheel(event):
            # Check if the canvas has content to scroll
            try:
                self.preview_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except tk.TclError:
                pass  # Ignore scroll errors when no content
        
        def _on_shift_mousewheel(event):
            # Horizontal scrolling with Shift+mouse wheel
            try:
                self.preview_canvas.xview_scroll(int(-1*(event.delta/120)), "units")
            except tk.TclError:
                pass  # Ignore scroll errors when no content
        
        # Bind mousewheel events to multiple widgets to ensure they work
        self.preview_canvas.bind("<MouseWheel>", _on_mousewheel)
        self.preview_canvas.bind("<Shift-MouseWheel>", _on_shift_mousewheel)
        
        # Also bind to the preview frame and canvas frame to catch mouse wheel events when hovering
        preview_frame.bind("<MouseWheel>", _on_mousewheel)
        preview_frame.bind("<Shift-MouseWheel>", _on_shift_mousewheel)
        canvas_frame.bind("<MouseWheel>", _on_mousewheel)
        canvas_frame.bind("<Shift-MouseWheel>", _on_shift_mousewheel)
        
        # Bind to the main window as well for global scrolling
        def _on_enter(event):
            # Give focus to canvas when mouse enters and bind wheel events
            self.preview_canvas.focus_set()
            
        def _on_leave(event):
            # Keep focus on canvas even when mouse leaves for consistent scrolling
            pass
        
        # Bind mouse enter/leave events
        self.preview_canvas.bind("<Enter>", _on_enter)
        self.preview_canvas.bind("<Leave>", _on_leave)
        canvas_frame.bind("<Enter>", _on_enter)
        preview_frame.bind("<Enter>", _on_enter)
        
        # For Windows, also bind to Button-4 and Button-5 for better compatibility
        def _on_button4(event):
            try:
                self.preview_canvas.yview_scroll(-1, "units")
            except tk.TclError:
                pass
                
        def _on_button5(event):
            try:
                self.preview_canvas.yview_scroll(1, "units")
            except tk.TclError:
                pass
        
        # Bind additional scroll events for better cross-platform compatibility
        self.preview_canvas.bind("<Button-4>", _on_button4)
        self.preview_canvas.bind("<Button-5>", _on_button5)
        
        # Make sure canvas gets initial focus
        self.root.after(100, lambda: self.preview_canvas.focus_set())
        
        # Make canvas focusable for keyboard navigation
        self.preview_canvas.configure(takefocus=True)
        
        # Bind keyboard scrolling
        def _on_key_press(event):
            if event.keysym == "Up":
                self.preview_canvas.yview_scroll(-1, "units")
            elif event.keysym == "Down":
                self.preview_canvas.yview_scroll(1, "units")
            elif event.keysym == "Left":
                self.preview_canvas.xview_scroll(-1, "units")
            elif event.keysym == "Right":
                self.preview_canvas.xview_scroll(1, "units")
            elif event.keysym == "Prior":  # Page Up
                self.preview_canvas.yview_scroll(-10, "units")
            elif event.keysym == "Next":   # Page Down
                self.preview_canvas.yview_scroll(10, "units")
        
        self.preview_canvas.bind("<Key>", _on_key_press)
        
        # Focus canvas when clicked
        def _on_canvas_click(event):
            self.preview_canvas.focus_set()
        
        self.preview_canvas.bind("<Button-1>", _on_canvas_click)
        
        # Bind canvas resize to update scroll region
        self.preview_canvas.bind('<Configure>', self.on_canvas_configure)
    
    def on_canvas_configure(self, event):
        """Handle canvas resize events"""
        # Only handle canvas configure events, not child widget events
        if event.widget == self.preview_canvas:
            # Update canvas scroll region when canvas size changes
            if hasattr(self, 'preview_image') and self.preview_image:
                # Recalculate and redraw the image to fit the new canvas size
                self.update_canvas(self.preview_image)
    
    def create_action_buttons(self):
        """Create file controls"""
        file_frame = ttk.LabelFrame(self.scrollable_frame, text="File Controls", padding=10)
        file_frame.pack(fill=tk.X, pady=10)
        
        # Save image button
        save_btn = ttk.Button(file_frame, text="Save Image", command=self.save_image)
        save_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Copy to clipboard button
        copy_btn = ttk.Button(file_frame, text="Copy to Clipboard", command=self.copy_to_clipboard)
        copy_btn.pack(side=tk.LEFT, padx=5)
    
    def load_fonts(self):
        """Load available fonts from user-specified directories only"""
        all_fonts = {}  # Dictionary to store font name -> font path mapping
        
        # Load fonts from all specified directories
        for font_dir in self.font_directories:
            if os.path.exists(font_dir):
                # Mark if this is the default fonts directory
                is_default_dir = os.path.basename(font_dir).lower() == "fonts"
                
                for root, dirs, files in os.walk(font_dir):
                    for file in files:
                        if file.lower().endswith(('.ttf', '.otf')):
                            font_path = os.path.join(root, file)
                            font_name = os.path.splitext(file)[0]
                            # Clean up font name (remove version numbers, etc.)
                            font_name = self._clean_font_name(font_name)
                            
                            # Add directory indicator if not from default directory
                            if not is_default_dir:
                                dir_name = os.path.basename(font_dir)
                                font_name = f"{font_name} ({dir_name})"
                            
                            # Avoid duplicate names by adding a counter if needed
                            original_name = font_name
                            counter = 1
                            while font_name in all_fonts:
                                font_name = f"{original_name} ({counter})"
                                counter += 1
                            
                            all_fonts[font_name] = font_path
        
        # Store the font mapping and create sorted list
        self.font_paths = all_fonts
        self.available_fonts = sorted(all_fonts.keys(), key=str.lower)
        
        # Set default font
        if self.available_fonts:
            # Just use the first available font as default
            self.font_var.set(self.available_fonts[0])
            self.font_display_label.config(text=self.available_fonts[0])
    
    def open_font_selector(self):
        """Open the font selection window"""
        font_window = tk.Toplevel(self.root)
        font_window.title("Select Font")
        font_window.geometry("500x600")
        font_window.transient(self.root)
        font_window.grab_set()
        
        # Search frame
        search_frame = ttk.Frame(font_window, padding=10)
        search_frame.pack(fill=tk.X)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var, width=30)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Font list frame with scrollbar
        list_frame = ttk.Frame(font_window, padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas and scrollbar for font list
        canvas = tk.Canvas(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Font selection variable
        selected_font = tk.StringVar(value=self.font_var.get())
        
        # Create radio buttons for all fonts
        font_buttons = []
        
        def update_font_list():
            # Clear existing buttons
            for widget in scrollable_frame.winfo_children():
                widget.destroy()
            font_buttons.clear()
            
            # Filter fonts based on search
            search_term = search_var.get().lower()
            if search_term:
                filtered_fonts = [font for font in self.available_fonts 
                                if search_term in font.lower()]
            else:
                filtered_fonts = self.available_fonts
            
            # Create radio buttons for filtered fonts
            for font in filtered_fonts:
                rb = ttk.Radiobutton(scrollable_frame, text=font, 
                                   variable=selected_font, value=font)
                rb.pack(anchor=tk.W, pady=1)
                font_buttons.append(rb)
        
        # Bind search to update function
        search_var.trace('w', lambda *args: update_font_list())
        
        # Initial population
        update_font_list()
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Button frame
        button_frame = ttk.Frame(font_window, padding=10)
        button_frame.pack(fill=tk.X)
        
        def set_font():
            chosen_font = selected_font.get()
            if chosen_font and chosen_font in self.available_fonts:
                self.font_var.set(chosen_font)
                self.font_display_label.config(text=chosen_font)
                self.update_preview()
            font_window.destroy()
        
        def cancel():
            font_window.destroy()
        
        ttk.Button(button_frame, text="Set Font", command=set_font).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=cancel).pack(side=tk.RIGHT)
        
        # Focus on search entry
        search_entry.focus()
        
        # Cleanup mousewheel binding when window closes
        def on_close():
            canvas.unbind_all("<MouseWheel>")
            font_window.destroy()
        
        font_window.protocol("WM_DELETE_WINDOW", on_close)
    
    def _clean_font_name(self, font_name):
        """Clean up font name by removing common suffixes and patterns"""
        # Remove common font weight/style suffixes
        suffixes_to_remove = [
            'Regular', 'Bold', 'Italic', 'Light', 'Medium', 'Heavy', 'Black',
            'Thin', 'ExtraLight', 'SemiBold', 'ExtraBold', 'UltraLight',
            'DemiBold', 'Book', 'Roman', 'Oblique', 'Condensed', 'Extended'
        ]
        
        # Remove version numbers and common patterns
        font_name = re.sub(r'\s*\d+\.\d+.*$', '', font_name)
        font_name = re.sub(r'\s*\(.*\)$', '', font_name)
        
        # Remove weight/style suffixes
        for suffix in suffixes_to_remove:
            if font_name.endswith(' ' + suffix):
                font_name = font_name[:-len(' ' + suffix)]
            elif font_name.endswith('-' + suffix):
                font_name = font_name[:-len('-' + suffix)]
        
        return font_name.strip()
    
    def load_preset_list(self):
        """Load available presets from the presets directory"""
        preset_files = []
        presets_dir = "presets"
        if os.path.exists(presets_dir):
            for file in os.listdir(presets_dir):
                if file.lower().endswith('.json'):
                    preset_name = os.path.splitext(file)[0]
                    preset_files.append(preset_name)
        
        # Add "None" as the first option
        preset_options = ["None"] + sorted(preset_files)
        self.preset_combo['values'] = preset_options
        self.preset_var.set("None")
    
    def load_selected_preset(self, event=None):
        """Load the selected preset from the dropdown"""
        preset_name = self.preset_var.get()
        if preset_name == "None" or not preset_name:
            return
        
        preset_file = os.path.join("presets", f"{preset_name}.json")
        if os.path.exists(preset_file):
            try:
                with open(preset_file, 'r') as f:
                    preset_data = json.load(f)
                
                # Apply settings (same as load_preset but without file dialog)
                self.text_var.set(preset_data.get('text', 'Sample Text'))
                self.font_size_var.set(preset_data.get('font_size', 48))
                self.font_var.set(preset_data.get('font', ''))
                self.text_color_var.set(preset_data.get('text_color', '#000000'))
                self.text_color2_var.set(preset_data.get('text_color2', '#FFFFFF'))
                self.text_outline_color_var.set(preset_data.get('text_outline_color', '#FFFFFF'))
                self.text_glow_color_var.set(preset_data.get('text_glow_color', '#0000FF'))
                # Convert old glow intensity scale (0-400) to new scale (0-100) for backward compatibility
                old_glow_intensity = preset_data.get('glow_intensity', 50)
                new_glow_intensity = min(100, old_glow_intensity // 4) if old_glow_intensity > 100 else old_glow_intensity
                self.glow_intensity_var.set(new_glow_intensity)
                self.glow_radius_var.set(preset_data.get('glow_radius', 3))
                self.glow_enabled_var.set(preset_data.get('glow_enabled', True))
                self.outline_thickness_var.set(preset_data.get('outline_thickness', 2))
                self.text_gradient_var.set(preset_data.get('text_gradient', 'None'))
                self.text_gradient_angle_var.set(preset_data.get('text_gradient_angle', 0))
                self.text_gradient_size_var.set(preset_data.get('text_gradient_size', 100))
                self.bg_opacity_var.set(preset_data.get('bg_opacity', preset_data.get('bg_transparency', 100)))  # backward compatibility
                self.bg_color_var.set(preset_data.get('bg_color', '#FFFFFF'))
                self.bg_color2_var.set(preset_data.get('bg_color2', '#000000'))
                self.bg_gradient_var.set(preset_data.get('bg_gradient', 'None'))
                self.bg_gradient_angle_var.set(preset_data.get('bg_gradient_angle', 0))
                self.bg_gradient_size_var.set(preset_data.get('bg_gradient_size', 100))
                self.image_width_var.set(preset_data.get('image_width', 800))
                self.image_height_var.set(preset_data.get('image_height', 400))
                self.margin_left_var.set(preset_data.get('margin_left', 10))
                self.margin_right_var.set(preset_data.get('margin_right', 10))
                self.margin_top_var.set(preset_data.get('margin_top', 10))
                self.margin_bottom_var.set(preset_data.get('margin_bottom', 10))
                self.alignment_var.set(preset_data.get('alignment', 'center'))
                
                # Update color buttons and preview
                self.update_color_buttons()
                self.update_preview()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load preset '{preset_name}': {str(e)}")
                self.preset_var.set("None")
    
    def upload_font(self):
        """Upload a new font file to a selected directory"""
        # First, let user choose which directory to upload to
        if len(self.font_directories) == 1:
            target_dir = self.font_directories[0]
        else:
            # Create a simple selection dialog for multiple directories
            dir_window = tk.Toplevel(self.root)
            dir_window.title("Select Target Directory")
            dir_window.geometry("400x300")
            dir_window.transient(self.root)
            dir_window.grab_set()
            
            ttk.Label(dir_window, text="Select a directory to upload the font to:", padding=10).pack()
            
            selected_dir = tk.StringVar()
            
            # Create radio buttons for each directory
            for directory in self.font_directories:
                display_name = os.path.basename(directory) if directory != os.path.abspath("fonts") else "Default (fonts)"
                ttk.Radiobutton(dir_window, text=f"{display_name}\n{directory}", 
                              variable=selected_dir, value=directory).pack(anchor=tk.W, padx=20, pady=5)
            
            # Set default selection
            if self.font_directories:
                selected_dir.set(self.font_directories[0])
            
            # Buttons
            button_frame = ttk.Frame(dir_window)
            button_frame.pack(pady=20)
            
            result = {"cancelled": False, "directory": None}
            
            def select_and_continue():
                result["directory"] = selected_dir.get()
                dir_window.destroy()
            
            def cancel():
                result["cancelled"] = True
                dir_window.destroy()
            
            ttk.Button(button_frame, text="Continue", command=select_and_continue).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Cancel", command=cancel).pack(side=tk.LEFT, padx=5)
            
            # Wait for dialog to close
            dir_window.wait_window()
            
            if result["cancelled"] or not result["directory"]:
                return
            
            target_dir = result["directory"]
        
        # Now select the font file
        file_path = filedialog.askopenfilename(
            title="Select Font File",
            filetypes=[("Font files", "*.ttf *.otf"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Ensure target directory exists
                os.makedirs(target_dir, exist_ok=True)
                
                # Copy font to target directory
                filename = os.path.basename(file_path)
                dest_path = os.path.join(target_dir, filename)
                
                # Check if file already exists
                if os.path.exists(dest_path):
                    if not messagebox.askyesno("File Exists", f"Font '{filename}' already exists in this directory. Overwrite?"):
                        return
                
                shutil.copy2(file_path, dest_path)
                
                # Reload fonts
                self.load_fonts()
                
                # Try to select the new font
                font_name = os.path.splitext(filename)[0]
                font_name = self._clean_font_name(font_name)
                
                # Find the font in the available fonts list
                for available_font in self.available_fonts:
                    if font_name.lower() in available_font.lower():
                        self.font_var.set(available_font)
                        self.font_display_label.config(text=available_font)
                        break
                
                messagebox.showinfo("Success", f"Font '{filename}' uploaded successfully to {os.path.basename(target_dir)}!")
                self.update_preview()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to upload font: {str(e)}")
    
    def load_font_directories_config(self):
        """Load font directories from configuration file"""
        config_file = "font_directories.json"
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    data = json.load(f)
                    self.font_directories = data.get('directories', [])
                    # Validate that directories exist, remove non-existent ones
                    self.font_directories = [d for d in self.font_directories if os.path.exists(d)]
            else:
                self.font_directories = []
        except Exception as e:
            print(f"Warning: Could not load font directories config: {e}")
            self.font_directories = []
    
    def save_font_directories_config(self):
        """Save font directories to configuration file"""
        config_file = "font_directories.json"
        try:
            with open(config_file, 'w') as f:
                json.dump({'directories': self.font_directories}, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save font directories config: {e}")
    
    def manage_font_directories(self):
        """Open the font directory management window"""
        dir_window = tk.Toplevel(self.root)
        dir_window.title("Manage Font Directories")
        dir_window.geometry("600x500")
        dir_window.transient(self.root)
        dir_window.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(dir_window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        ttk.Label(main_frame, text="Font Directories", font=("Arial", 12, "bold")).pack(pady=(0, 5))
        ttk.Label(main_frame, text="Manage directories where fonts will be loaded from:").pack(pady=(0, 10))
        
        # Directory list frame
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create listbox with scrollbar
        list_scrollbar = ttk.Scrollbar(list_frame)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        dir_listbox = tk.Listbox(list_frame, yscrollcommand=list_scrollbar.set)
        dir_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scrollbar.config(command=dir_listbox.yview)
        
        # Populate listbox
        def refresh_list():
            dir_listbox.delete(0, tk.END)
            for directory in self.font_directories:
                display_name = directory
                if directory == os.path.abspath("fonts"):
                    display_name += " (Default)"
                dir_listbox.insert(tk.END, display_name)
        
        refresh_list()
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        # Add directory button
        def add_directory():
            directory = filedialog.askdirectory(title="Select Font Directory")
            if directory and directory not in self.font_directories:
                self.font_directories.append(directory)
                refresh_list()
        
        # Remove directory button
        def remove_directory():
            selection = dir_listbox.curselection()
            if selection:
                index = selection[0]
                directory = self.font_directories[index]
                
                # Don't allow removing the default fonts directory if it's the only one
                if len(self.font_directories) == 1 and directory == os.path.abspath("fonts"):
                    messagebox.showwarning("Cannot Remove", "Cannot remove the default fonts directory when it's the only one. Add another directory first.")
                    return
                
                if messagebox.askyesno("Confirm Removal", f"Remove directory:\n{directory}"):
                    self.font_directories.pop(index)
                    refresh_list()
        
        # Browse to directory button
        def browse_directory():
            selection = dir_listbox.curselection()
            if selection:
                index = selection[0]
                directory = self.font_directories[index]
                if os.path.exists(directory):
                    if platform.system() == "Windows":
                        os.startfile(directory)
                    elif platform.system() == "Darwin":  # macOS
                        subprocess.run(["open", directory])
                    else:  # Linux
                        subprocess.run(["xdg-open", directory])
                else:
                    messagebox.showerror("Error", f"Directory does not exist:\n{directory}")
        
        ttk.Button(button_frame, text="Add Directory", command=add_directory).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Remove Selected", command=remove_directory).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Browse Selected", command=browse_directory).pack(side=tk.LEFT, padx=5)
        
        # Bottom buttons
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=(20, 0))
        
        def save_and_reload():
            self.save_font_directories_config()
            self.load_fonts()
            self.update_directory_info()
            messagebox.showinfo("Success", "Font directories saved and fonts reloaded!")
            dir_window.destroy()
        
        def cancel():
            # Reload from config to undo any changes
            self.load_font_directories_config()
            dir_window.destroy()
        
        ttk.Button(bottom_frame, text="Save & Reload Fonts", command=save_and_reload).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(bottom_frame, text="Cancel", command=cancel).pack(side=tk.RIGHT)
    
    def update_directory_info(self):
        """Update the directory info label"""
        if hasattr(self, 'directories_info_label'):
            count = len(self.font_directories)
            if count == 1:
                self.directories_info_label.config(text="1 directory")
            else:
                self.directories_info_label.config(text=f"{count} directories")
    
    def choose_color(self, color_var, button):
        """Open color chooser dialog"""
        color = colorchooser.askcolor(color=color_var.get())[1]
        if color:
            color_var.set(color)
            button.configure(bg=color)
            self.update_preview()
    
    def update_color_buttons(self):
        """Update color button appearances"""
        self.text_color_btn.configure(bg=self.text_color_var.get())
        self.text_color2_btn.configure(bg=self.text_color2_var.get())
        self.outline_color_btn.configure(bg=self.text_outline_color_var.get())
        self.glow_color_btn.configure(bg=self.text_glow_color_var.get())
        self.bg_color_btn.configure(bg=self.bg_color_var.get())
        self.bg_color2_btn.configure(bg=self.bg_color2_var.get())
    
    def hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple with caching"""
        # Check cache first
        if hex_color in self._color_cache:
            return self._color_cache[hex_color]
        
        # Convert color
        try:
            hex_color_clean = hex_color.lstrip('#')
            if len(hex_color_clean) != 6:
                # Invalid hex color, return black as fallback
                rgb = (0, 0, 0)
            else:
                rgb = tuple(int(hex_color_clean[i:i+2], 16) for i in (0, 2, 4))
        except (ValueError, TypeError):
            # Return black as fallback for any conversion errors
            rgb = (0, 0, 0)
        
        # Cache the result, but limit cache size
        if len(self._color_cache) >= self._color_cache_max_size:
            # Remove oldest color from cache (simple FIFO)
            oldest_key = next(iter(self._color_cache))
            del self._color_cache[oldest_key]
        
        self._color_cache[hex_color] = rgb
        return rgb
    
    def get_font_path(self, font_name):
        """Get the path to a font file"""
        # Check if we have a direct mapping to the font
        if hasattr(self, 'font_paths') and font_name in self.font_paths:
            return self.font_paths[font_name]
        
        # Fallback: check custom fonts directory
        custom_path = os.path.join("fonts", f"{font_name}.ttf")
        if os.path.exists(custom_path):
            return custom_path
        
        custom_path = os.path.join("fonts", f"{font_name}.otf")
        if os.path.exists(custom_path):
            return custom_path
        
        # For unknown fonts, return None (will use default)
        return None
    
    def get_cached_font(self, font_name, font_size):
        """Get a cached font or create and cache a new one"""
        cache_key = (font_name, font_size)
        
        # Check if font is already cached
        if cache_key in self._font_cache:
            return self._font_cache[cache_key]
        
        # Get font path
        font_path = self.get_font_path(font_name)
        
        try:
            if font_path:
                font = ImageFont.truetype(font_path, font_size)
            else:
                # Use default font if no custom font is available
                font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        # Cache the font, but limit cache size
        if len(self._font_cache) >= self._font_cache_max_size:
            # Remove oldest font from cache (simple FIFO)
            oldest_key = next(iter(self._font_cache))
            del self._font_cache[oldest_key]
        
        self._font_cache[cache_key] = font
        return font
    
    def create_gradient(self, size, color1, color2, gradient_type, angle, gradient_size=100):
        """Create a gradient image with controllable gradient size - optimized with NumPy"""
        width, height = size
        
        # Validate input parameters to prevent division by zero
        if width <= 0 or height <= 0:
            return Image.new('RGBA', (max(1, width), max(1, height)), color1)
        
        try:
            gradient_size = max(1, min(100, gradient_size))  # Clamp to 1-100
            angle = angle % 360 if angle else 0  # Handle None/empty angle
        except (ValueError, TypeError):
            gradient_size = 100
            angle = 0
        
        # Use NumPy for vectorized operations - much faster than pixel-by-pixel
        try:
            # Create coordinate arrays
            x = np.arange(width, dtype=np.float32)
            y = np.arange(height, dtype=np.float32)
            X, Y = np.meshgrid(x, y)
            
            if gradient_type == "None":
                # Solid color - create uniform array
                factor = np.zeros((height, width), dtype=np.float32)
            elif gradient_type == "Linear":
                # Linear gradient with proper angle support and gradient size control
                angle_rad = math.radians(angle)
                dx = math.cos(angle_rad)
                dy = math.sin(angle_rad)
                
                # Center coordinates
                half_width = width / 2
                half_height = height / 2
                
                # Calculate relative positions
                rel_x = X - half_width
                rel_y = Y - half_height
                
                # Calculate projection onto gradient direction
                projection = rel_x * dx + rel_y * dy
                
                # Find the maximum projection distance
                max_proj = abs(half_width * dx) + abs(half_height * dy)
                if max_proj == 0:
                    max_proj = 1
                
                # Normalize to 0-1 range
                factor = (projection + max_proj) / (2 * max_proj)
                factor = np.clip(factor, 0, 1)
                
                # Apply gradient size control
                if gradient_size < 100:
                    size_factor = gradient_size / 100.0
                    center = 0.5
                    gradient_range = size_factor
                    
                    # Vectorized gradient size control
                    mask_low = factor < (center - gradient_range / 2)
                    mask_high = factor > (center + gradient_range / 2)
                    mask_mid = ~(mask_low | mask_high)
                    
                    factor[mask_low] = 0
                    factor[mask_high] = 1
                    factor[mask_mid] = (factor[mask_mid] - (center - gradient_range / 2)) / max(gradient_range, 0.001)
                    
            elif gradient_type == "Radial":
                # Radial gradient from center with gradient size control
                center_x, center_y = width // 2, height // 2
                max_distance = max(width, height) // 2
                
                if max_distance == 0:
                    max_distance = 1
                
                # Calculate distance from center
                distance = np.sqrt((X - center_x) ** 2 + (Y - center_y) ** 2)
                factor = np.minimum(distance / max_distance, 1.0)
                
                # Apply gradient size control
                if gradient_size < 100:
                    size_factor = gradient_size / 100.0
                    factor = np.minimum(factor / max(size_factor, 0.001), 1.0)
                    
            elif gradient_type == "Circular":
                # Circular gradient with angle offset and gradient size control
                center_x, center_y = width // 2, height // 2
                
                # Calculate angle from center
                dx = X - center_x
                dy = Y - center_y
                pixel_angle = np.degrees(np.arctan2(dy, dx)) + angle
                pixel_angle = pixel_angle % 360
                
                # Use angle as factor
                factor = pixel_angle / 360
                
                # Apply gradient size control
                if gradient_size < 100:
                    size_factor = gradient_size / 100.0
                    transition_point = 0.5
                    gradient_range = size_factor
                    
                    mask_low = factor < (transition_point - gradient_range / 2)
                    mask_high = factor > (transition_point + gradient_range / 2)
                    mask_mid = ~(mask_low | mask_high)
                    
                    factor[mask_low] = 0
                    factor[mask_high] = 1
                    factor[mask_mid] = (factor[mask_mid] - (transition_point - gradient_range / 2)) / max(gradient_range, 0.001)
            else:
                # Default to solid color
                factor = np.zeros((height, width), dtype=np.float32)
            
            # Convert colors to numpy arrays for vectorized blending
            color1_array = np.array(color1[:3], dtype=np.float32)
            color2_array = np.array(color2[:3], dtype=np.float32)
            
            # Vectorized color blending
            factor_3d = factor[:, :, np.newaxis]  # Add channel dimension
            rgb = color1_array * (1 - factor_3d) + color2_array * factor_3d
            rgb = np.clip(rgb, 0, 255).astype(np.uint8)
            
            # Handle alpha channel
            if len(color1) > 3 and len(color2) > 3:
                alpha1, alpha2 = color1[3], color2[3]
                alpha = alpha1 * (1 - factor) + alpha2 * factor
                alpha = np.clip(alpha, 0, 255).astype(np.uint8)
                rgba = np.dstack([rgb, alpha])
            else:
                alpha = np.full((height, width), 255, dtype=np.uint8)
                rgba = np.dstack([rgb, alpha])
            
            # Convert to PIL Image
            return Image.fromarray(rgba, 'RGBA')
            
        except ImportError:
            # Fallback to original pixel-by-pixel method if NumPy is not available
            return self._create_gradient_fallback(size, color1, color2, gradient_type, angle, gradient_size)
        except Exception:
            # Any other error, fallback to original method
            return self._create_gradient_fallback(size, color1, color2, gradient_type, angle, gradient_size)
    
    def _create_gradient_fallback(self, size, color1, color2, gradient_type, angle, gradient_size=100):
        """Fallback gradient creation method for when NumPy is not available"""
        width, height = size
        image = Image.new('RGBA', size, (0, 0, 0, 0))
        
        if gradient_type == "None":
            return Image.new('RGBA', size, color1)
        
        # Original pixel-by-pixel implementation as fallback
        for y in range(height):
            for x in range(width):
                if gradient_type == "Linear":
                    angle_rad = math.radians(angle)
                    dx = math.cos(angle_rad)
                    dy = math.sin(angle_rad)
                    
                    half_width = width / 2
                    half_height = height / 2
                    
                    rel_x = x - half_width
                    rel_y = y - half_height
                    
                    projection = rel_x * dx + rel_y * dy
                    max_proj = abs(half_width * dx) + abs(half_height * dy)
                    if max_proj == 0:
                        max_proj = 1
                    
                    factor = (projection + max_proj) / (2 * max_proj)
                    factor = max(0, min(1, factor))
                    
                elif gradient_type == "Radial":
                    center_x, center_y = width // 2, height // 2
                    max_distance = max(width, height) // 2
                    if max_distance == 0:
                        max_distance = 1
                    
                    distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
                    factor = min(distance / max_distance, 1.0)
                    
                elif gradient_type == "Circular":
                    center_x, center_y = width // 2, height // 2
                    dx = x - center_x
                    dy = y - center_y
                    pixel_angle = math.degrees(math.atan2(dy, dx)) + angle
                    pixel_angle = pixel_angle % 360
                    factor = pixel_angle / 360
                else:
                    factor = 0
                
                # Apply gradient size control
                if gradient_size < 100:
                    size_factor = gradient_size / 100.0
                    center = 0.5
                    gradient_range = size_factor
                    
                    if factor < center - gradient_range / 2:
                        factor = 0
                    elif factor > center + gradient_range / 2:
                        factor = 1
                    else:
                        factor = (factor - (center - gradient_range / 2)) / max(gradient_range, 0.001)
                
                # Blend colors
                r = int(color1[0] * (1 - factor) + color2[0] * factor)
                g = int(color1[1] * (1 - factor) + color2[1] * factor)
                b = int(color1[2] * (1 - factor) + color2[2] * factor)
                a = int(color1[3] * (1 - factor) + color2[3] * factor) if len(color1) > 3 else 255
                
                image.putpixel((x, y), (r, g, b, a))
        
        return image
    
    def update_preview_debounced(self):
        """Debounced version of update_preview to improve performance"""
        # Cancel any pending preview update
        if self._preview_update_id:
            self.root.after_cancel(self._preview_update_id)
        
        # Schedule a new preview update
        self._preview_update_id = self.root.after(self._preview_update_delay, self._do_update_preview)
    
    def _do_update_preview(self):
        """Internal method that actually performs the preview update"""
        self._preview_update_id = None
        self.update_preview()
    
    def update_preview(self):
        """Update the preview image"""
        try:
            # Get current values with safe fallbacks
            text = self.text_var.get()
            if not text:
                text = "Sample Text"
            
            # Safe value retrieval with fallbacks
            font_size = self.safe_get_numeric(self.font_size_var, 48, 1)
            width = self.safe_get_numeric(self.image_width_var, 800, 1)
            height = self.safe_get_numeric(self.image_height_var, 400, 1)
            
            # Create image
            image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
            draw = ImageDraw.Draw(image)
            
            # Create background
            bg_color1 = self.hex_to_rgb(self.bg_color_var.get())
            bg_color2 = self.hex_to_rgb(self.bg_color2_var.get())
            bg_opacity = self.safe_get_numeric(self.bg_opacity_var, 100, 0, 100)
            
            # Apply opacity to background colors
            bg_alpha = int(255 * bg_opacity / 100)
            bg_color1_rgba = bg_color1 + (bg_alpha,)
            bg_color2_rgba = bg_color2 + (bg_alpha,)
            
            if self.bg_gradient_var.get() != "None":
                bg_gradient_angle = self.safe_get_numeric(self.bg_gradient_angle_var, 0)
                bg_gradient_size = self.safe_get_numeric(self.bg_gradient_size_var, 100, 1, 100)
                    
                bg_gradient = self.create_gradient(
                    (width, height), bg_color1_rgba, bg_color2_rgba,
                    self.bg_gradient_var.get(), bg_gradient_angle, bg_gradient_size
                )
                image = Image.alpha_composite(image, bg_gradient)
            else:
                bg_image = Image.new('RGBA', (width, height), bg_color1_rgba)
                image = Image.alpha_composite(image, bg_image)
            
            # Load font with caching
            font_name = self.font_var.get()
            font = self.get_cached_font(font_name, font_size)
            
            # Get text size
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Calculate position based on alignment and margins
            margin_left = self.safe_get_numeric(self.margin_left_var, 10, 0)
            margin_right = self.safe_get_numeric(self.margin_right_var, 10, 0)
            margin_top = self.safe_get_numeric(self.margin_top_var, 10, 0)
            margin_bottom = self.safe_get_numeric(self.margin_bottom_var, 10, 0)
            
            # Calculate available space for text positioning
            available_width = width - margin_left - margin_right
            available_height = height - margin_top - margin_bottom
            
            alignment = self.alignment_var.get()
            if alignment == "nw":  # Top-left
                x, y = margin_left, margin_top
            elif alignment == "n":  # Top-center
                x, y = margin_left + (available_width - text_width) // 2, margin_top
            elif alignment == "ne":  # Top-right
                x, y = width - margin_right - text_width, margin_top
            elif alignment == "w":  # Middle-left
                x, y = margin_left, margin_top + (available_height - text_height) // 2
            elif alignment == "center":  # Center
                x, y = margin_left + (available_width - text_width) // 2, margin_top + (available_height - text_height) // 2
            elif alignment == "e":  # Middle-right
                x, y = width - margin_right - text_width, margin_top + (available_height - text_height) // 2
            elif alignment == "sw":  # Bottom-left
                x, y = margin_left, height - margin_bottom - text_height
            elif alignment == "s":  # Bottom-center
                x, y = margin_left + (available_width - text_width) // 2, height - margin_bottom - text_height
            elif alignment == "se":  # Bottom-right
                x, y = width - margin_right - text_width, height - margin_bottom - text_height
            else:
                x, y = margin_left + (available_width - text_width) // 2, margin_top + (available_height - text_height) // 2
            
            # Create separate layers for each effect
            glow_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            outline_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            
            # Draw glow effect first (bottom layer)
            glow_color = self.hex_to_rgb(self.text_glow_color_var.get())
            glow_radius = self.safe_get_numeric(self.glow_radius_var, 5, 0)
            glow_intensity = self.safe_get_numeric(self.glow_intensity_var, 19, 0, 100)
            glow_enabled = self.glow_enabled_var.get()
            
            if glow_enabled and glow_radius > 0 and glow_intensity > 0:
                # Create glow mask using the same text
                glow_mask = Image.new('L', (width, height), 0)
                glow_mask_draw = ImageDraw.Draw(glow_mask)
                glow_mask_draw.text((x, y), text, font=font, fill=255)
                
                # Apply Gaussian blur for smooth glow effect
                blur_radius = max(1, glow_radius * 1.5)
                glow_mask = glow_mask.filter(ImageFilter.GaussianBlur(radius=blur_radius))
                
                # Create colored glow image with proper intensity
                # Scale the percentage (0-100) to the internal range (0-400) for intensity calculation
                actual_intensity = max(1, glow_intensity * 4)  # Prevent zero intensity
                glow_alpha = min(255, int(255 * actual_intensity / 100))  # Clamp to 255
                glow_colored = Image.new('RGBA', (width, height), glow_color + (0,))
                
                # Convert mask to alpha channel with intensity applied
                glow_pixels = list(glow_mask.getdata())
                glow_alpha_data = []
                
                for pixel_value in glow_pixels:
                    alpha = int((pixel_value / 255) * glow_alpha) if glow_alpha > 0 else 0
                    glow_alpha_data.append(alpha)
                
                # Create alpha channel from processed data
                alpha_channel = Image.new('L', (width, height))
                alpha_channel.putdata(glow_alpha_data)
                
                # Apply the alpha channel to create the final glow
                glow_colored.putalpha(alpha_channel)
                
                # Set the glow layer
                glow_layer = glow_colored
            
            # Draw outline on separate layer (middle layer)
            outline_color = self.hex_to_rgb(self.text_outline_color_var.get())
            outline_thickness = self.safe_get_numeric(self.outline_thickness_var, 2, 0)
            
            if outline_thickness > 0:
                outline_draw = ImageDraw.Draw(outline_layer)
                for adj in range(-outline_thickness, outline_thickness + 1):
                    for adj2 in range(-outline_thickness, outline_thickness + 1):
                        if adj != 0 or adj2 != 0:
                            outline_draw.text((x + adj, y + adj2), text, font=font, fill=outline_color + (255,))
            # Create a separate layer for the main text to ensure it appears on top
            main_text_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            main_text_draw = ImageDraw.Draw(main_text_layer)
            
            # Draw main text on the separate layer
            text_color1 = self.hex_to_rgb(self.text_color_var.get())
            
            if self.text_gradient_var.get() != "None":
                # Create text with gradient
                text_color2 = self.hex_to_rgb(self.text_color2_var.get())
                
                # Create a mask from the text
                text_mask = Image.new('L', (width, height), 0)
                mask_draw = ImageDraw.Draw(text_mask)
                mask_draw.text((x, y), text, font=font, fill=255)
                
                # Calculate text bounding box for gradient sizing - use the actual position
                text_bbox = draw.textbbox((x, y), text, font=font)
                text_left = text_bbox[0]
                text_top = text_bbox[1]
                text_right = text_bbox[2]
                text_bottom = text_bbox[3]
                
                text_actual_width = text_right - text_left
                text_actual_height = text_bottom - text_top
                
                # Create gradient for just the text size
                text_gradient_angle = self.safe_get_numeric(self.text_gradient_angle_var, 0)
                text_gradient_size = self.safe_get_numeric(self.text_gradient_size_var, 100, 1, 100)
                    
                text_gradient = self.create_gradient(
                    (text_actual_width, text_actual_height),
                    text_color1 + (255,),
                    text_color2 + (255,),
                    self.text_gradient_var.get(),
                    text_gradient_angle,
                    text_gradient_size
                )
                
                # Create a full-size gradient image and paste the text-sized gradient at the actual text bounds
                full_gradient = Image.new('RGBA', (width, height), (0, 0, 0, 0))
                full_gradient.paste(text_gradient, (text_left, text_top))
                
                # Apply the text mask to the gradient
                full_gradient.putalpha(text_mask)
                
                # Composite the gradient text
                main_text_layer = Image.alpha_composite(main_text_layer, full_gradient)
            else:
                # Draw solid color text
                main_text_draw.text((x, y), text, font=font, fill=text_color1 + (255,))
            
            # Composite all layers in correct order: glow -> outline -> main text
            final_text_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            
            # Add glow first (bottom layer)
            if glow_enabled and glow_radius > 0 and glow_intensity > 0:
                final_text_layer = Image.alpha_composite(final_text_layer, glow_layer)
            
            # Add outline second (middle layer) 
            if outline_thickness > 0:
                final_text_layer = Image.alpha_composite(final_text_layer, outline_layer)
            
            # Add main text last (top layer)
            final_text_layer = Image.alpha_composite(final_text_layer, main_text_layer)
            
            # Composite final text layer with background
            image = Image.alpha_composite(image, final_text_layer)
            
            # Store the current image
            self.preview_image = image
            
            # Update canvas
            self.update_canvas(image)
            
        except ZeroDivisionError:
            # Silent handling of division by zero - common when sliders are at zero
            pass
        except (ValueError, tk.TclError) as e:
            # Silent handling of invalid numeric values - common during typing
            if "floating point" in str(e) or "invalid literal" in str(e):
                pass
            else:
                print(f"Preview update error: {e}")
        except Exception as e:
            # Only print unexpected errors
            print(f"Preview update error: {e}")
    
    def update_canvas(self, image):
        """Update the canvas with the new image"""
        try:
            # Resize image to fit canvas while maintaining aspect ratio
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                # Canvas not ready yet
                self.root.after(100, lambda: self.update_canvas(image))
                return
            
            # Calculate scaling
            img_width, img_height = image.size
            
            # Prevent division by zero
            if img_width <= 0 or img_height <= 0:
                return
                
            scale_x = canvas_width / img_width
            scale_y = canvas_height / img_height
            scale = min(scale_x, scale_y, 1.0)  # Don't scale up
            
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            # Resize image for display
            display_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            output = io.BytesIO()
            display_image.save(output, format='PNG')
            output.seek(0)
            
            photo = tk.PhotoImage(data=output.getvalue())
            
            # Clear canvas and display image
            self.preview_canvas.delete("all")
            
            # Center the image on the canvas
            image_x = max(canvas_width // 2, new_width // 2)
            image_y = max(canvas_height // 2, new_height // 2)
            
            self.preview_canvas.create_image(
                image_x, image_y,
                image=photo, anchor=tk.CENTER
            )
            
            # Store reference to prevent garbage collection
            self.preview_canvas.image = photo
            
            # Update scroll region to encompass the image
            scroll_width = max(canvas_width, new_width)
            scroll_height = max(canvas_height, new_height)
            self.preview_canvas.configure(scrollregion=(0, 0, scroll_width, scroll_height))
            
            # Enable scrollbars if image is larger than canvas
            if new_width > canvas_width or new_height > canvas_height:
                # Update the canvas to show scrollbars if needed
                self.preview_canvas.update_idletasks()
                
                # Center the view if image is larger than canvas
                if new_width > canvas_width:
                    # Center horizontally
                    self.preview_canvas.xview_moveto(0.5 - (canvas_width / new_width / 2))
                if new_height > canvas_height:
                    # Center vertically  
                    self.preview_canvas.yview_moveto(0.5 - (canvas_height / new_height / 2))
            
        except ZeroDivisionError:
            # Silent handling of division by zero - common when image dimensions are zero
            pass
        except (ValueError, tk.TclError) as e:
            # Silent handling of invalid values during canvas updates
            pass
        except Exception as e:
            # Only print unexpected errors
            print(f"Canvas update error: {e}")
    
    def save_image(self):
        """Save the current image"""
        if not self.preview_image:
            messagebox.showwarning("Warning", "No image to save!")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                # Convert RGBA to RGB if saving as JPEG
                if file_path.lower().endswith('.jpg') or file_path.lower().endswith('.jpeg'):
                    # Create white background for JPEG
                    bg = Image.new('RGB', self.preview_image.size, (255, 255, 255))
                    bg.paste(self.preview_image, mask=self.preview_image.split()[-1])
                    bg.save(file_path, quality=95)
                else:
                    self.preview_image.save(file_path)
                
                messagebox.showinfo("Success", f"Image saved as {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image: {str(e)}")
    
    def copy_to_clipboard(self):
        """Copy image to clipboard"""
        if not self.preview_image:
            messagebox.showwarning("Warning", "No image to copy!")
            return
        
        try:
            # For Windows, try using win32clipboard if available
            if platform.system() == "Windows" and win32clipboard is not None:
                try:
                    win32clipboard.OpenClipboard()
                    win32clipboard.EmptyClipboard()
                    
                    # Convert to bitmap format for Windows clipboard
                    output = io.BytesIO()
                    self.preview_image.save(output, format='BMP')
                    data = output.getvalue()[14:]  # Remove BMP header
                    
                    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
                    win32clipboard.CloseClipboard()
                    
                    messagebox.showinfo("Success", "Image copied to clipboard!")
                    return
                    
                except ImportError:
                    # Fall back to alternative method
                    pass
            
            # Alternative method: save to temp file and use system clipboard
            temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            self.preview_image.save(temp_file.name)
            temp_file.close()
            
            # Try to copy using system commands
            if platform.system() == "Windows":
                try:
                    # Use PowerShell to copy image to clipboard
                    cmd = f'powershell.exe -command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Clipboard]::SetImage([System.Drawing.Image]::FromFile(\'{temp_file.name}\'))"'
                    subprocess.run(cmd, shell=True, check=True)
                    messagebox.showinfo("Success", "Image copied to clipboard!")
                except subprocess.CalledProcessError:
                    messagebox.showinfo("Info", "Could not copy to clipboard. Image saved to temporary file instead.")
            else:
                messagebox.showinfo("Info", "Clipboard copy not fully supported on this platform. Please save the image instead.")
            
            # Clean up temp file
            try:
                os.unlink(temp_file.name)
            except:
                pass
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy to clipboard: {str(e)}")
            messagebox.showinfo("Alternative", "You can save the image and manually copy it to clipboard.")
    
    def save_preset(self):
        """Save current settings as a preset"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir="presets"
        )
        
        if file_path:
            try:
                preset_data = {
                    'text': self.text_var.get(),
                    'font_size': self.font_size_var.get(),
                    'font': self.font_var.get(),
                    'text_color': self.text_color_var.get(),
                    'text_color2': self.text_color2_var.get(),
                    'text_outline_color': self.text_outline_color_var.get(),
                    'text_glow_color': self.text_glow_color_var.get(),
                    'glow_intensity': self.glow_intensity_var.get(),
                    'glow_radius': self.glow_radius_var.get(),
                    'glow_enabled': self.glow_enabled_var.get(),
                    'outline_thickness': self.outline_thickness_var.get(),
                    'text_gradient': self.text_gradient_var.get(),
                    'text_gradient_angle': self.text_gradient_angle_var.get(),
                    'text_gradient_size': self.text_gradient_size_var.get(),
                    'bg_opacity': self.bg_opacity_var.get(),
                    'bg_color': self.bg_color_var.get(),
                    'bg_color2': self.bg_color2_var.get(),
                    'bg_gradient': self.bg_gradient_var.get(),
                    'bg_gradient_angle': self.bg_gradient_angle_var.get(),
                    'bg_gradient_size': self.bg_gradient_size_var.get(),
                    'image_width': self.image_width_var.get(),
                    'image_height': self.image_height_var.get(),
                    'margin_left': self.margin_left_var.get(),
                    'margin_right': self.margin_right_var.get(),
                    'margin_top': self.margin_top_var.get(),
                    'margin_bottom': self.margin_bottom_var.get(),
                    'alignment': self.alignment_var.get()
                }
                
                with open(file_path, 'w') as f:
                    json.dump(preset_data, f, indent=2)
                
                messagebox.showinfo("Success", f"Preset saved as {file_path}")
                # Refresh the preset dropdown to include the new preset
                self.load_preset_list()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save preset: {str(e)}")

def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = FontImageMaker(root)
    
    # Bind window resize to update preview
    root.bind('<Configure>', lambda e: app.update_preview() if e.widget == root else None)
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main()