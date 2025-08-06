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
import glob
import tempfile
import math

class FontImageMaker:
    def __init__(self, root):
        self.root = root
        self.root.title("Font Image Maker")
        
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
        
        # Update color button appearances
        self.update_color_buttons()
        
        # Load system fonts
        self.load_fonts()
        
        # Load available presets
        self.load_preset_list()
        
        # Initialize preview
        self.update_preview()
    
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
        
        # Current preview image
        self.preview_image = None
    
    def create_directories(self):
        """Create necessary directories"""
        os.makedirs("fonts", exist_ok=True)
        os.makedirs("presets", exist_ok=True)
    
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
    
    def create_main_frames(self):
        """Create main layout frames with calculated sidebar width"""
        # Calculate required sidebar width based on actual content
        required_width = self.calculate_required_sidebar_width()
        
        # Left panel for controls with scrollbar
        self.left_frame = ttk.Frame(self.root, width=required_width)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=3, pady=3)
        self.left_frame.pack_propagate(False)
        
        # Create canvas and scrollbar for left frame
        canvas_width = required_width - 20  # Account for scrollbar
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
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind("<MouseWheel>", _on_mousewheel)
        
        # Right panel for preview - this will take remaining space
        self.right_frame = ttk.Frame(self.root)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=3, pady=3)
    
    def calculate_required_sidebar_width(self):
        """Calculate the minimum required width for sidebar content"""
        # Base measurements for typical UI elements (in pixels)
        label_widths = {
            "Text:": 40,
            "Preset:": 50,
            "Size:": 35,
            "Font:": 35,
            "Primary Color:": 85,
            "Secondary Color (Optional):": 180,
            "Gradient Type:": 85,
            "Gradient Angle:": 90,
            "Gradient Width:": 90,
            "Outline Color:": 85,
            "Outline Thickness:": 110,
            "Glow Color:": 75,
            "Glow Intensity:": 90,
            "Glow Radius:": 85,
            "Opacity:": 55,
            "Gradient Angle:": 90,  # Background
            "Image Size:": 75,
            "Left:": 35,
            "Right:": 40,
            "Top:": 30,
            "Bottom:": 50,
            "Text Alignment:": 95
        }
        
        control_widths = {
            "entry_small": 60,      # Font size, margins
            "entry_medium": 120,    # Text input, preset combo
            "entry_large": 180,     # Full width entries
            "button_small": 80,     # Color buttons
            "button_medium": 100,   # Select Font, Save Preset
            "combo_small": 100,     # Gradient type
            "combo_medium": 120,    # Preset dropdown
            "scale_small": 80,      # Small sliders
            "scale_medium": 120,    # Medium sliders
            "spinbox": 80,          # Image size spinboxes
            "checkbox": 90,         # Enable Glow
            "radiobutton": 80       # Alignment buttons (3 per row)
        }
        
        # Calculate maximum width needed for each section
        max_widths = []
        
        # Text Settings section
        text_section_rows = [
            ("Text:", "entry_large"),  # 40 + 180 = 220
            ("Preset:", "combo_medium", "button_medium"),  # 50 + 120 + 100 = 270
            ("Size:", "scale_medium", "entry_small"),  # 35 + 120 + 60 = 215
            ("Font:", "entry_large", "button_medium", "button_medium"),  # 35 + 180 + 100 + 100 = 415
            ("Primary Color:", "button_small"),  # 85 + 80 = 165
            ("Secondary Color (Optional):", "button_small"),  # 180 + 80 = 260
            ("Gradient Type:", "combo_small"),  # 85 + 100 = 185
            ("Gradient Angle:", "scale_medium", "entry_small"),  # 90 + 120 + 60 = 270
            ("Gradient Width:", "scale_medium", "entry_small"),  # 90 + 120 + 60 = 270
            ("Outline Color:", "button_small"),  # 85 + 80 = 165
            ("Outline Thickness:", "scale_medium", "entry_small"),  # 110 + 120 + 60 = 290
            ("Glow Color:", "button_small", "checkbox"),  # 75 + 80 + 90 = 245
            ("Glow Intensity:", "scale_medium", "entry_small"),  # 90 + 120 + 60 = 270
            ("Glow Radius:", "scale_medium", "entry_small"),  # 85 + 120 + 60 = 265
        ]
        
        for row in text_section_rows:
            row_width = label_widths.get(row[0], 50)  # Label width
            for control in row[1:]:
                row_width += control_widths.get(control, 50)
            max_widths.append(row_width)
        
        # Background Settings section  
        bg_section_rows = [
            ("Opacity:", "scale_medium", "entry_small"),  # 55 + 120 + 60 = 235
            ("Primary Color:", "button_small"),  # 85 + 80 = 165
            ("Secondary Color (Optional):", "button_small"),  # 180 + 80 = 260
            ("Gradient Type:", "combo_small"),  # 85 + 100 = 185
            ("Gradient Angle:", "scale_medium", "entry_small"),  # 90 + 120 + 60 = 270
            ("Gradient Width:", "scale_medium", "entry_small"),  # 90 + 120 + 60 = 270
        ]
        
        for row in bg_section_rows:
            row_width = label_widths.get(row[0], 50)
            for control in row[1:]:
                row_width += control_widths.get(control, 50)
            max_widths.append(row_width)
        
        # General Settings section
        general_section_rows = [
            ("Image Size:", "spinbox", "spinbox"),  # 75 + 80 + 80 = 235
            ("Left:", "scale_small", "entry_small"),  # 35 + 80 + 60 = 175
            ("Text Alignment:", "radiobutton", "radiobutton", "radiobutton"),  # 95 + 80*3 = 335
        ]
        
        for row in general_section_rows:
            row_width = label_widths.get(row[0], 50)
            for control in row[1:]:
                row_width += control_widths.get(control, 50)
            max_widths.append(row_width)
        
        # Get the maximum width needed
        content_width = max(max_widths)
        
        # Add padding and margins
        frame_padding = 20  # LabelFrame padding (10px each side)
        grid_spacing = 10   # Space between grid columns
        scrollbar_width = 20
        outer_padding = 6   # Frame padding (3px each side)
        
        total_width = content_width + frame_padding + grid_spacing + scrollbar_width + outer_padding
        
        # Ensure minimum usable width
        min_width = 250
        calculated_width = max(min_width, total_width)
        
        print(f"Calculated sidebar width: {calculated_width}px (content: {content_width}px)")
        return calculated_width
    
    def create_text_controls(self):
        """Create text customization controls"""
        text_frame = ttk.LabelFrame(self.scrollable_frame, text="Text Settings", padding=10)
        text_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Text input
        ttk.Label(text_frame, text="Text:").grid(row=0, column=0, sticky=tk.W, pady=2)
        text_entry = ttk.Entry(text_frame, textvariable=self.text_var, width=30)
        text_entry.grid(row=0, column=1, columnspan=2, sticky=tk.EW, pady=2)
        text_entry.bind('<KeyRelease>', lambda e: self.update_preview())
        
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
                              variable=self.font_size_var, command=lambda v: self.update_preview())
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
        
        # Text colors
        ttk.Label(text_frame, text="Primary Color:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.text_color_btn = tk.Button(text_frame, width=10, command=lambda: self.choose_color(self.text_color_var, self.text_color_btn))
        self.text_color_btn.grid(row=4, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(text_frame, text="Secondary Color (Optional):").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.text_color2_btn = tk.Button(text_frame, width=10, command=lambda: self.choose_color(self.text_color2_var, self.text_color2_btn))
        self.text_color2_btn.grid(row=5, column=1, sticky=tk.W, pady=2)
        
        # Text gradient
        ttk.Label(text_frame, text="Gradient Type:").grid(row=6, column=0, sticky=tk.W, pady=2)
        gradient_combo = ttk.Combobox(text_frame, textvariable=self.text_gradient_var, 
                                    values=["None", "Linear", "Radial", "Circular"], state="readonly", width=15)
        gradient_combo.grid(row=6, column=1, sticky=tk.W, pady=2)
        gradient_combo.bind('<<ComboboxSelected>>', lambda e: self.update_preview())
        
        # Gradient angle
        ttk.Label(text_frame, text="Gradient Angle:").grid(row=7, column=0, sticky=tk.W, pady=2)
        gradient_angle_frame = ttk.Frame(text_frame)
        gradient_angle_frame.grid(row=7, column=1, columnspan=2, sticky=tk.EW, pady=2)
        
        angle_scale = ttk.Scale(gradient_angle_frame, from_=0, to=360, orient=tk.HORIZONTAL, 
                              variable=self.text_gradient_angle_var, command=lambda v: self.update_preview())
        angle_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(gradient_angle_frame, text="°").pack(side=tk.RIGHT, padx=(1, 5))
        
        self.gradient_angle_entry = ttk.Entry(gradient_angle_frame, textvariable=self.text_gradient_angle_var, width=6)
        self.gradient_angle_entry.pack(side=tk.RIGHT, padx=(5, 0))
        self.gradient_angle_entry.bind('<Return>', lambda e: self.update_preview())
        self.gradient_angle_entry.bind('<FocusOut>', lambda e: self.update_preview())
        
        # Gradient size
        ttk.Label(text_frame, text="Gradient Width:").grid(row=8, column=0, sticky=tk.W, pady=2)
        gradient_size_frame = ttk.Frame(text_frame)
        gradient_size_frame.grid(row=8, column=1, columnspan=2, sticky=tk.EW, pady=2)
        
        gradient_size_scale = ttk.Scale(gradient_size_frame, from_=0, to=100, orient=tk.HORIZONTAL, 
                                      variable=self.text_gradient_size_var, command=lambda v: self.update_preview())
        gradient_size_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(gradient_size_frame, text="%").pack(side=tk.RIGHT, padx=(1, 5))
        
        self.gradient_size_entry = ttk.Entry(gradient_size_frame, textvariable=self.text_gradient_size_var, width=6)
        self.gradient_size_entry.pack(side=tk.RIGHT, padx=(5, 0))
        self.gradient_size_entry.bind('<Return>', lambda e: self.update_preview())
        self.gradient_size_entry.bind('<FocusOut>', lambda e: self.update_preview())
        
        # Text outline
        ttk.Label(text_frame, text="Outline Color:").grid(row=9, column=0, sticky=tk.W, pady=2)
        self.outline_color_btn = tk.Button(text_frame, width=10, command=lambda: self.choose_color(self.text_outline_color_var, self.outline_color_btn))
        self.outline_color_btn.grid(row=9, column=1, sticky=tk.W, pady=2)
        
        # Outline thickness
        ttk.Label(text_frame, text="Outline Thickness:").grid(row=10, column=0, sticky=tk.W, pady=2)
        outline_frame = ttk.Frame(text_frame)
        outline_frame.grid(row=10, column=1, columnspan=2, sticky=tk.EW, pady=2)
        
        outline_scale = ttk.Scale(outline_frame, from_=0, to=10, orient=tk.HORIZONTAL,
                                variable=self.outline_thickness_var, command=lambda v: self.update_preview())
        outline_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(outline_frame, text="px").pack(side=tk.RIGHT, padx=(1, 5))
        
        self.outline_entry = ttk.Entry(outline_frame, textvariable=self.outline_thickness_var, width=6)
        self.outline_entry.pack(side=tk.RIGHT, padx=(5, 0))
        self.outline_entry.bind('<Return>', lambda e: self.update_preview())
        self.outline_entry.bind('<FocusOut>', lambda e: self.update_preview())
        
        # Text glow
        ttk.Label(text_frame, text="Glow Color:").grid(row=11, column=0, sticky=tk.W, pady=2)
        self.glow_color_btn = tk.Button(text_frame, width=10, command=lambda: self.choose_color(self.text_glow_color_var, self.glow_color_btn))
        self.glow_color_btn.grid(row=11, column=1, sticky=tk.W, pady=2)
        
        # Glow enable checkbox
        self.glow_enabled_cb = ttk.Checkbutton(text_frame, text="Enable Glow", variable=self.glow_enabled_var, command=self.update_preview)
        self.glow_enabled_cb.grid(row=11, column=2, sticky=tk.W, pady=2)
        
        # Glow intensity
        ttk.Label(text_frame, text="Glow Intensity:").grid(row=12, column=0, sticky=tk.W, pady=2)
        glow_intensity_frame = ttk.Frame(text_frame)
        glow_intensity_frame.grid(row=12, column=1, columnspan=2, sticky=tk.EW, pady=2)
        
        glow_intensity_scale = ttk.Scale(glow_intensity_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                       variable=self.glow_intensity_var, command=lambda v: self.update_preview())
        glow_intensity_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(glow_intensity_frame, text="%").pack(side=tk.RIGHT, padx=(1, 5))
        
        self.glow_intensity_entry = ttk.Entry(glow_intensity_frame, textvariable=self.glow_intensity_var, width=6)
        self.glow_intensity_entry.pack(side=tk.RIGHT, padx=(5, 0))
        self.glow_intensity_entry.bind('<Return>', lambda e: self.update_preview())
        self.glow_intensity_entry.bind('<FocusOut>', lambda e: self.update_preview())
        
        # Glow radius
        ttk.Label(text_frame, text="Glow Radius:").grid(row=13, column=0, sticky=tk.W, pady=2)
        glow_radius_frame = ttk.Frame(text_frame)
        glow_radius_frame.grid(row=13, column=1, columnspan=2, sticky=tk.EW, pady=2)
        
        glow_radius_scale = ttk.Scale(glow_radius_frame, from_=0, to=20, orient=tk.HORIZONTAL,
                                    variable=self.glow_radius_var, command=lambda v: self.update_preview())
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
        
        # Background colors
        ttk.Label(bg_frame, text="Primary Color:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.bg_color_btn = tk.Button(bg_frame, width=10, command=lambda: self.choose_color(self.bg_color_var, self.bg_color_btn))
        self.bg_color_btn.grid(row=1, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(bg_frame, text="Secondary Color (Optional):").grid(row=2, column=0, sticky=tk.W, pady=2)
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
        ttk.Label(general_frame, text="Text Alignment:").grid(row=5, column=0, sticky=tk.NW, pady=5)
        
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
        
        # Create canvas for preview
        self.preview_canvas = tk.Canvas(preview_frame, bg="white", width=600, height=400)
        self.preview_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbars for canvas
        h_scroll = ttk.Scrollbar(preview_frame, orient=tk.HORIZONTAL, command=self.preview_canvas.xview)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.preview_canvas.configure(xscrollcommand=h_scroll.set)
        
        v_scroll = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview_canvas.yview)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.preview_canvas.configure(yscrollcommand=v_scroll.set)
    
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
        """Load available fonts from system and custom directories"""
        all_fonts = {}  # Dictionary to store font name -> font path mapping
        
        # System font directories by platform
        system_font_dirs = []
        if platform.system() == "Windows":
            system_font_dirs = [
                os.path.join(os.environ.get('WINDIR', 'C:/Windows'), 'Fonts'),
                os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Microsoft', 'Windows', 'Fonts')
            ]
        elif platform.system() == "Darwin":  # macOS
            system_font_dirs = [
                '/System/Library/Fonts',
                '/Library/Fonts',
                os.path.join(os.path.expanduser('~'), 'Library', 'Fonts')
            ]
        else:  # Linux
            system_font_dirs = [
                '/usr/share/fonts',
                '/usr/local/share/fonts',
                os.path.join(os.path.expanduser('~'), '.fonts'),
                os.path.join(os.path.expanduser('~'), '.local', 'share', 'fonts')
            ]
        
        # Load system fonts
        for font_dir in system_font_dirs:
            if os.path.exists(font_dir):
                for root, dirs, files in os.walk(font_dir):
                    for file in files:
                        if file.lower().endswith(('.ttf', '.otf')):
                            font_path = os.path.join(root, file)
                            font_name = os.path.splitext(file)[0]
                            # Clean up font name (remove version numbers, etc.)
                            font_name = self._clean_font_name(font_name)
                            all_fonts[font_name] = font_path
        
        # Load custom fonts from fonts directory
        custom_fonts_dir = "fonts"
        if os.path.exists(custom_fonts_dir):
            for file in os.listdir(custom_fonts_dir):
                if file.lower().endswith(('.ttf', '.otf')):
                    font_path = os.path.join(custom_fonts_dir, file)
                    font_name = os.path.splitext(file)[0] + " (Custom)"
                    all_fonts[font_name] = font_path
        
        # Store the font mapping and create sorted list
        self.font_paths = all_fonts
        self.available_fonts = sorted(all_fonts.keys(), key=str.lower)
        
        # Set default font
        if self.available_fonts:
            # Try to find Arial or similar common font first
            default_fonts = ['Arial', 'Helvetica', 'Times New Roman', 'Courier New']
            default_set = False
            for default_font in default_fonts:
                matching_fonts = [f for f in self.available_fonts if default_font.lower() in f.lower()]
                if matching_fonts:
                    self.font_var.set(matching_fonts[0])
                    self.font_display_label.config(text=matching_fonts[0])
                    default_set = True
                    break
            
            if not default_set:
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
        import re
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
        """Upload a new font file"""
        file_path = filedialog.askopenfilename(
            title="Select Font File",
            filetypes=[("Font files", "*.ttf *.otf"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Copy font to fonts directory
                filename = os.path.basename(file_path)
                dest_path = os.path.join("fonts", filename)
                shutil.copy2(file_path, dest_path)
                
                # Reload fonts
                self.load_fonts()
                
                # Select the new font (with Custom suffix)
                font_name = os.path.splitext(filename)[0] + " (Custom)"
                if font_name in self.available_fonts:
                    self.font_var.set(font_name)
                    self.font_display_label.config(text=font_name)
                else:
                    # Fallback to base name if custom suffix not found
                    base_name = os.path.splitext(filename)[0]
                    if base_name in self.available_fonts:
                        self.font_var.set(base_name)
                        self.font_display_label.config(text=base_name)
                
                messagebox.showinfo("Success", f"Font uploaded successfully!")
                self.update_preview()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to upload font: {str(e)}")
    
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
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
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
    
    def create_gradient(self, size, color1, color2, gradient_type, angle, gradient_size=100):
        """Create a gradient image with controllable gradient size"""
        width, height = size
        image = Image.new('RGBA', size, (0, 0, 0, 0))
        
        if gradient_type == "None":
            # Solid color
            image = Image.new('RGBA', size, color1)
        elif gradient_type == "Linear":
            # Linear gradient with proper angle support and gradient size control
            
            # Convert angle to radians
            angle_rad = math.radians(angle)
            
            # Calculate the direction vector
            dx = math.cos(angle_rad)
            dy = math.sin(angle_rad)
            
            # Calculate the projection range
            half_width = width / 2
            half_height = height / 2
            
            # Find the maximum projection distance
            max_proj = abs(half_width * dx) + abs(half_height * dy)
            
            # Calculate gradient size factor (0-1, where 0 is very sharp, 1 is full gradient)
            size_factor = gradient_size / 100.0
            
            for y in range(height):
                for x in range(width):
                    # Calculate position relative to center
                    rel_x = x - half_width
                    rel_y = y - half_height
                    
                    # Calculate projection onto gradient direction
                    projection = rel_x * dx + rel_y * dy
                    
                    # Normalize to 0-1 range
                    factor = (projection + max_proj) / (2 * max_proj)
                    factor = max(0, min(1, factor))
                    
                    # Apply gradient size control
                    if size_factor < 1.0:
                        # Compress the gradient range
                        center = 0.5
                        gradient_range = size_factor
                        
                        # Map factor to compressed range around center
                        if factor < center - gradient_range / 2:
                            factor = 0
                        elif factor > center + gradient_range / 2:
                            factor = 1
                        else:
                            # Remap to 0-1 within the gradient range
                            factor = (factor - (center - gradient_range / 2)) / gradient_range
                    
                    # Blend colors
                    r = int(color1[0] * (1 - factor) + color2[0] * factor)
                    g = int(color1[1] * (1 - factor) + color2[1] * factor)
                    b = int(color1[2] * (1 - factor) + color2[2] * factor)
                    a = int(color1[3] * (1 - factor) + color2[3] * factor) if len(color1) > 3 else 255
                    
                    image.putpixel((x, y), (r, g, b, a))
                    
        elif gradient_type == "Radial":
            # Radial gradient from center with gradient size control
            center_x, center_y = width // 2, height // 2
            max_distance = max(width, height) // 2
            
            # Calculate gradient size factor
            size_factor = gradient_size / 100.0
            
            for y in range(height):
                for x in range(width):
                    distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
                    factor = min(distance / max_distance, 1.0)
                    
                    # Apply gradient size control
                    if size_factor < 1.0:
                        # Compress the gradient range
                        gradient_range = size_factor
                        
                        if factor > gradient_range:
                            factor = 1
                        else:
                            # Remap to 0-1 within the gradient range
                            factor = factor / gradient_range
                    
                    r = int(color1[0] * (1 - factor) + color2[0] * factor)
                    g = int(color1[1] * (1 - factor) + color2[1] * factor)
                    b = int(color1[2] * (1 - factor) + color2[2] * factor)
                    a = int(color1[3] * (1 - factor) + color2[3] * factor) if len(color1) > 3 else 255
                    
                    image.putpixel((x, y), (r, g, b, a))
                    
        elif gradient_type == "Circular":
            # Circular gradient with angle offset and gradient size control
            center_x, center_y = width // 2, height // 2
            
            # Calculate gradient size factor
            size_factor = gradient_size / 100.0
            
            for y in range(height):
                for x in range(width):
                    # Calculate angle from center
                    dx = x - center_x
                    dy = y - center_y
                    pixel_angle = math.degrees(math.atan2(dy, dx)) + angle
                    pixel_angle = pixel_angle % 360
                    
                    # Use angle as factor
                    factor = pixel_angle / 360
                    
                    # Apply gradient size control
                    if size_factor < 1.0:
                        # Create sharp transitions by compressing the gradient range
                        gradient_range = size_factor
                        transition_point = 0.5  # Center point for the transition
                        
                        if factor < transition_point - gradient_range / 2:
                            factor = 0
                        elif factor > transition_point + gradient_range / 2:
                            factor = 1
                        else:
                            # Remap to 0-1 within the gradient range
                            factor = (factor - (transition_point - gradient_range / 2)) / gradient_range
                    
                    r = int(color1[0] * (1 - factor) + color2[0] * factor)
                    g = int(color1[1] * (1 - factor) + color2[1] * factor)
                    b = int(color1[2] * (1 - factor) + color2[2] * factor)
                    a = int(color1[3] * (1 - factor) + color2[3] * factor) if len(color1) > 3 else 255
                    
                    image.putpixel((x, y), (r, g, b, a))
        
        return image
    
    def update_preview(self):
        """Update the preview image"""
        try:
            # Get current values
            text = self.text_var.get()
            if not text:
                text = "Sample Text"
            
            font_size = self.font_size_var.get()
            width = self.image_width_var.get()
            height = self.image_height_var.get()
            
            # Create image
            image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
            draw = ImageDraw.Draw(image)
            
            # Create background
            bg_color1 = self.hex_to_rgb(self.bg_color_var.get())
            bg_color2 = self.hex_to_rgb(self.bg_color2_var.get())
            bg_opacity = self.bg_opacity_var.get()
            
            # Apply opacity to background colors
            bg_alpha = int(255 * bg_opacity / 100)
            bg_color1_rgba = bg_color1 + (bg_alpha,)
            bg_color2_rgba = bg_color2 + (bg_alpha,)
            
            if self.bg_gradient_var.get() != "None":
                bg_gradient = self.create_gradient(
                    (width, height), bg_color1_rgba, bg_color2_rgba,
                    self.bg_gradient_var.get(), self.bg_gradient_angle_var.get(), self.bg_gradient_size_var.get()
                )
                image = Image.alpha_composite(image, bg_gradient)
            else:
                bg_image = Image.new('RGBA', (width, height), bg_color1_rgba)
                image = Image.alpha_composite(image, bg_image)
            
            # Load font
            font_name = self.font_var.get()
            font_path = self.get_font_path(font_name)
            
            try:
                if font_path:
                    font = ImageFont.truetype(font_path, font_size)
                else:
                    # Try to use system font or default
                    try:
                        if platform.system() == "Windows":
                            font = ImageFont.truetype("arial.ttf", font_size)
                        else:
                            font = ImageFont.load_default()
                    except:
                        font = ImageFont.load_default()
            except:
                font = ImageFont.load_default()
            
            # Get text size
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Calculate position based on alignment and margins
            margin_left = self.margin_left_var.get()
            margin_right = self.margin_right_var.get()
            margin_top = self.margin_top_var.get()
            margin_bottom = self.margin_bottom_var.get()
            
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
            glow_radius = self.glow_radius_var.get()
            glow_intensity = self.glow_intensity_var.get()
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
                actual_intensity = glow_intensity * 4  # Convert 0-100% to 0-400 range
                glow_alpha = int(255 * actual_intensity / 100)
                glow_colored = Image.new('RGBA', (width, height), glow_color + (0,))
                
                # Convert mask to alpha channel with intensity applied
                glow_pixels = list(glow_mask.getdata())
                glow_alpha_data = []
                
                for pixel_value in glow_pixels:
                    alpha = int((pixel_value / 255) * glow_alpha)
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
            outline_thickness = self.outline_thickness_var.get()
            
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
                text_gradient = self.create_gradient(
                    (text_actual_width, text_actual_height),
                    text_color1 + (255,),
                    text_color2 + (255,),
                    self.text_gradient_var.get(),
                    self.text_gradient_angle_var.get(),
                    self.text_gradient_size_var.get()
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
            
        except Exception as e:
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
            scale_x = canvas_width / img_width
            scale_y = canvas_height / img_height
            scale = min(scale_x, scale_y, 1.0)  # Don't scale up
            
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            # Resize image
            display_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage using a different method
            import io
            output = io.BytesIO()
            display_image.save(output, format='PNG')
            output.seek(0)
            
            photo = tk.PhotoImage(data=output.getvalue())
            
            # Clear canvas and display image
            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(
                canvas_width // 2, canvas_height // 2,
                image=photo, anchor=tk.CENTER
            )
            
            # Store reference to prevent garbage collection
            self.preview_canvas.image = photo
            
            # Update scroll region
            self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))
            
        except Exception as e:
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
            if platform.system() == "Windows":
                try:
                    import win32clipboard
                    
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
            import tempfile
            temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            self.preview_image.save(temp_file.name)
            temp_file.close()
            
            # Try to copy using system commands
            if platform.system() == "Windows":
                import subprocess
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