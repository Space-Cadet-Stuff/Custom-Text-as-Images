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

class FontImageMaker:
    def __init__(self, root):
        self.root = root
        self.root.title("Font Image Maker")
        self.root.geometry("1200x800")
        
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
        self.glow_intensity_var = tk.IntVar(value=75)  # Increased from 50 to 75
        self.glow_radius_var = tk.IntVar(value=5)      # Increased from 3 to 5
        self.outline_thickness_var = tk.IntVar(value=2) # pixels
        self.glow_enabled_var = tk.BooleanVar(value=True)  # glow on/off
        
        # Text gradient
        self.text_gradient_var = tk.StringVar(value="None")
        self.text_gradient_angle_var = tk.IntVar(value=0)
        
        # Background variables
        self.bg_opacity_var = tk.IntVar(value=100)
        self.bg_color_var = tk.StringVar(value="#FFFFFF")
        self.bg_color2_var = tk.StringVar(value="#000000")
        self.bg_gradient_var = tk.StringVar(value="None")
        self.bg_gradient_angle_var = tk.IntVar(value=0)
        
        # Image size
        self.image_width_var = tk.IntVar(value=800)
        self.image_height_var = tk.IntVar(value=400)
        
        # Alignment
        self.alignment_var = tk.StringVar(value="center")
        
        # Font
        self.font_var = tk.StringVar()
        
        # Available fonts list
        self.available_fonts = []
        
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
        """Create main layout frames"""
        # Left panel for controls with scrollbar
        self.left_frame = ttk.Frame(self.root, width=400)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        self.left_frame.pack_propagate(False)
        
        # Create canvas and scrollbar for left frame
        self.canvas = tk.Canvas(self.left_frame, width=380)
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
        
        # Right panel for preview
        self.right_frame = ttk.Frame(self.root)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def create_text_controls(self):
        """Create text customization controls"""
        text_frame = ttk.LabelFrame(self.scrollable_frame, text="Text Settings", padding=10)
        text_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Text input
        ttk.Label(text_frame, text="Text:").grid(row=0, column=0, sticky=tk.W, pady=2)
        text_entry = ttk.Entry(text_frame, textvariable=self.text_var, width=30)
        text_entry.grid(row=0, column=1, columnspan=2, sticky=tk.EW, pady=2)
        text_entry.bind('<KeyRelease>', lambda e: self.update_preview())
        
        # Font size slider
        ttk.Label(text_frame, text="Size:").grid(row=1, column=0, sticky=tk.W, pady=2)
        size_frame = ttk.Frame(text_frame)
        size_frame.grid(row=1, column=1, columnspan=2, sticky=tk.EW, pady=2)
        
        size_scale = ttk.Scale(size_frame, from_=8, to=200, orient=tk.HORIZONTAL,
                              variable=self.font_size_var, command=lambda v: self.update_preview())
        size_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.size_entry = ttk.Entry(size_frame, textvariable=self.font_size_var, width=6)
        self.size_entry.pack(side=tk.RIGHT, padx=(5, 0))
        self.size_entry.bind('<Return>', lambda e: self.update_preview())
        self.size_entry.bind('<FocusOut>', lambda e: self.update_preview())
        
        # Add unit label
        ttk.Label(size_frame, text="pt").pack(side=tk.RIGHT, padx=(1, 5))
        
        # Font selection
        ttk.Label(text_frame, text="Font:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.font_combo = ttk.Combobox(text_frame, textvariable=self.font_var, width=25, state="readonly")
        self.font_combo.grid(row=2, column=1, columnspan=2, sticky=tk.EW, pady=2)
        self.font_combo.bind('<<ComboboxSelected>>', lambda e: self.update_preview())
        
        # Upload font button
        upload_font_btn = ttk.Button(text_frame, text="Upload Font", command=self.upload_font)
        upload_font_btn.grid(row=3, column=1, pady=5)
        
        # Text colors
        ttk.Label(text_frame, text="Text Color:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.text_color_btn = tk.Button(text_frame, width=10, command=lambda: self.choose_color(self.text_color_var, self.text_color_btn))
        self.text_color_btn.grid(row=4, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(text_frame, text="Secondary Color:").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.text_color2_btn = tk.Button(text_frame, width=10, command=lambda: self.choose_color(self.text_color2_var, self.text_color2_btn))
        self.text_color2_btn.grid(row=5, column=1, sticky=tk.W, pady=2)
        
        # Text outline
        ttk.Label(text_frame, text="Outline Color:").grid(row=6, column=0, sticky=tk.W, pady=2)
        self.outline_color_btn = tk.Button(text_frame, width=10, command=lambda: self.choose_color(self.text_outline_color_var, self.outline_color_btn))
        self.outline_color_btn.grid(row=6, column=1, sticky=tk.W, pady=2)
        
        # Outline thickness
        ttk.Label(text_frame, text="Outline Thickness:").grid(row=7, column=0, sticky=tk.W, pady=2)
        outline_frame = ttk.Frame(text_frame)
        outline_frame.grid(row=7, column=1, columnspan=2, sticky=tk.EW, pady=2)
        
        outline_scale = ttk.Scale(outline_frame, from_=0, to=10, orient=tk.HORIZONTAL,
                                variable=self.outline_thickness_var, command=lambda v: self.update_preview())
        outline_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.outline_entry = ttk.Entry(outline_frame, textvariable=self.outline_thickness_var, width=6)
        self.outline_entry.pack(side=tk.RIGHT, padx=(5, 0))
        self.outline_entry.bind('<Return>', lambda e: self.update_preview())
        self.outline_entry.bind('<FocusOut>', lambda e: self.update_preview())
        
        ttk.Label(outline_frame, text="px").pack(side=tk.RIGHT, padx=(1, 5))
        
        # Text glow
        ttk.Label(text_frame, text="Glow Color:").grid(row=8, column=0, sticky=tk.W, pady=2)
        self.glow_color_btn = tk.Button(text_frame, width=10, command=lambda: self.choose_color(self.text_glow_color_var, self.glow_color_btn))
        self.glow_color_btn.grid(row=8, column=1, sticky=tk.W, pady=2)
        
        # Glow enable checkbox
        self.glow_enabled_cb = ttk.Checkbutton(text_frame, text="Enable Glow", variable=self.glow_enabled_var, command=self.update_preview)
        self.glow_enabled_cb.grid(row=8, column=2, sticky=tk.W, pady=2)
        
        # Glow intensity
        ttk.Label(text_frame, text="Glow Intensity:").grid(row=9, column=0, sticky=tk.W, pady=2)
        glow_intensity_frame = ttk.Frame(text_frame)
        glow_intensity_frame.grid(row=9, column=1, columnspan=2, sticky=tk.EW, pady=2)
        
        glow_intensity_scale = ttk.Scale(glow_intensity_frame, from_=0, to=400, orient=tk.HORIZONTAL,
                                       variable=self.glow_intensity_var, command=lambda v: self.update_preview())
        glow_intensity_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.glow_intensity_entry = ttk.Entry(glow_intensity_frame, textvariable=self.glow_intensity_var, width=6)
        self.glow_intensity_entry.pack(side=tk.RIGHT, padx=(5, 0))
        self.glow_intensity_entry.bind('<Return>', lambda e: self.update_preview())
        self.glow_intensity_entry.bind('<FocusOut>', lambda e: self.update_preview())
        
        ttk.Label(glow_intensity_frame, text="%").pack(side=tk.RIGHT, padx=(1, 5))
        
        # Glow radius
        ttk.Label(text_frame, text="Glow Radius:").grid(row=10, column=0, sticky=tk.W, pady=2)
        glow_radius_frame = ttk.Frame(text_frame)
        glow_radius_frame.grid(row=10, column=1, columnspan=2, sticky=tk.EW, pady=2)
        
        glow_radius_scale = ttk.Scale(glow_radius_frame, from_=0, to=20, orient=tk.HORIZONTAL,
                                    variable=self.glow_radius_var, command=lambda v: self.update_preview())
        glow_radius_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.glow_radius_entry = ttk.Entry(glow_radius_frame, textvariable=self.glow_radius_var, width=6)
        self.glow_radius_entry.pack(side=tk.RIGHT, padx=(5, 0))
        self.glow_radius_entry.bind('<Return>', lambda e: self.update_preview())
        self.glow_radius_entry.bind('<FocusOut>', lambda e: self.update_preview())
        
        ttk.Label(glow_radius_frame, text="px").pack(side=tk.RIGHT, padx=(1, 5))
        
        # Text gradient
        ttk.Label(text_frame, text="Gradient Type:").grid(row=11, column=0, sticky=tk.W, pady=2)
        gradient_combo = ttk.Combobox(text_frame, textvariable=self.text_gradient_var, 
                                    values=["None", "Linear", "Radial", "Circular"], state="readonly", width=15)
        gradient_combo.grid(row=11, column=1, sticky=tk.W, pady=2)
        gradient_combo.bind('<<ComboboxSelected>>', lambda e: self.update_preview())
        
        # Gradient angle
        ttk.Label(text_frame, text="Gradient Angle:").grid(row=12, column=0, sticky=tk.W, pady=2)
        gradient_angle_frame = ttk.Frame(text_frame)
        gradient_angle_frame.grid(row=12, column=1, columnspan=2, sticky=tk.EW, pady=2)
        
        angle_scale = ttk.Scale(gradient_angle_frame, from_=0, to=360, orient=tk.HORIZONTAL, 
                              variable=self.text_gradient_angle_var, command=lambda v: self.update_preview())
        angle_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.gradient_angle_entry = ttk.Entry(gradient_angle_frame, textvariable=self.text_gradient_angle_var, width=6)
        self.gradient_angle_entry.pack(side=tk.RIGHT, padx=(5, 0))
        self.gradient_angle_entry.bind('<Return>', lambda e: self.update_preview())
        self.gradient_angle_entry.bind('<FocusOut>', lambda e: self.update_preview())
        
        ttk.Label(gradient_angle_frame, text="°").pack(side=tk.RIGHT, padx=(1, 5))
        
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
        
        self.opacity_entry = ttk.Entry(opacity_frame, textvariable=self.bg_opacity_var, width=6)
        self.opacity_entry.pack(side=tk.RIGHT, padx=(5, 0))
        self.opacity_entry.bind('<Return>', lambda e: self.update_preview())
        self.opacity_entry.bind('<FocusOut>', lambda e: self.update_preview())
        
        ttk.Label(opacity_frame, text="%").pack(side=tk.RIGHT, padx=(1, 5))
        
        # Background colors
        ttk.Label(bg_frame, text="BG Color:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.bg_color_btn = tk.Button(bg_frame, width=10, command=lambda: self.choose_color(self.bg_color_var, self.bg_color_btn))
        self.bg_color_btn.grid(row=1, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(bg_frame, text="BG Secondary:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.bg_color2_btn = tk.Button(bg_frame, width=10, command=lambda: self.choose_color(self.bg_color2_var, self.bg_color2_btn))
        self.bg_color2_btn.grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # Background gradient
        ttk.Label(bg_frame, text="BG Gradient:").grid(row=3, column=0, sticky=tk.W, pady=2)
        bg_gradient_combo = ttk.Combobox(bg_frame, textvariable=self.bg_gradient_var,
                                       values=["None", "Linear", "Radial", "Circular"], state="readonly", width=15)
        bg_gradient_combo.grid(row=3, column=1, sticky=tk.W, pady=2)
        bg_gradient_combo.bind('<<ComboboxSelected>>', lambda e: self.update_preview())
        
        # Background gradient angle
        ttk.Label(bg_frame, text="BG Angle:").grid(row=4, column=0, sticky=tk.W, pady=2)
        bg_angle_frame = ttk.Frame(bg_frame)
        bg_angle_frame.grid(row=4, column=1, columnspan=2, sticky=tk.EW, pady=2)
        
        bg_angle_scale = ttk.Scale(bg_angle_frame, from_=0, to=360, orient=tk.HORIZONTAL,
                                 variable=self.bg_gradient_angle_var, command=lambda v: self.update_preview())
        bg_angle_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.bg_angle_entry = ttk.Entry(bg_angle_frame, textvariable=self.bg_gradient_angle_var, width=6)
        self.bg_angle_entry.pack(side=tk.RIGHT, padx=(5, 0))
        self.bg_angle_entry.bind('<Return>', lambda e: self.update_preview())
        self.bg_angle_entry.bind('<FocusOut>', lambda e: self.update_preview())
        
        ttk.Label(bg_angle_frame, text="°").pack(side=tk.RIGHT, padx=(1, 5))
        
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
        
        # Text alignment
        ttk.Label(general_frame, text="Text Alignment:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        alignment_frame = ttk.Frame(general_frame)
        alignment_frame.grid(row=1, column=1, columnspan=2, sticky=tk.EW, pady=5)
        
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
        """Create action buttons"""
        action_frame = ttk.Frame(self.scrollable_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        # Save image button
        save_btn = ttk.Button(action_frame, text="Save Image", command=self.save_image)
        save_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Copy to clipboard button
        copy_btn = ttk.Button(action_frame, text="Copy to Clipboard", command=self.copy_to_clipboard)
        copy_btn.pack(side=tk.LEFT, padx=5)
        
        # Save preset button
        save_preset_btn = ttk.Button(action_frame, text="Save Preset", command=self.save_preset)
        save_preset_btn.pack(side=tk.LEFT, padx=5)
        
        # Load preset button
        load_preset_btn = ttk.Button(action_frame, text="Load Preset", command=self.load_preset)
        load_preset_btn.pack(side=tk.LEFT, padx=5)
    
    def load_fonts(self):
        """Load available fonts"""
        # System fonts (basic list)
        system_fonts = ["Arial", "Times New Roman", "Courier New", "Helvetica", "Georgia", "Verdana"]
        
        # Custom fonts from fonts directory
        custom_fonts = []
        fonts_dir = "fonts"
        if os.path.exists(fonts_dir):
            for file in os.listdir(fonts_dir):
                if file.lower().endswith(('.ttf', '.otf')):
                    custom_fonts.append(os.path.splitext(file)[0])
        
        self.available_fonts = system_fonts + custom_fonts
        self.font_combo['values'] = self.available_fonts
        
        # Set default font
        if self.available_fonts:
            self.font_var.set(self.available_fonts[0])
    
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
                
                # Select the new font
                font_name = os.path.splitext(filename)[0]
                self.font_var.set(font_name)
                
                messagebox.showinfo("Success", f"Font '{font_name}' uploaded successfully!")
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
        # Check custom fonts first
        custom_path = os.path.join("fonts", f"{font_name}.ttf")
        if os.path.exists(custom_path):
            return custom_path
        
        custom_path = os.path.join("fonts", f"{font_name}.otf")
        if os.path.exists(custom_path):
            return custom_path
        
        # For system fonts, we'll use default
        return None
    
    def create_gradient(self, size, color1, color2, gradient_type, angle):
        """Create a gradient image"""
        width, height = size
        image = Image.new('RGBA', size, (0, 0, 0, 0))
        
        if gradient_type == "None":
            # Solid color
            image = Image.new('RGBA', size, color1)
        elif gradient_type == "Linear":
            # Linear gradient with proper angle support
            import math
            
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
                    
                    # Blend colors
                    r = int(color1[0] * (1 - factor) + color2[0] * factor)
                    g = int(color1[1] * (1 - factor) + color2[1] * factor)
                    b = int(color1[2] * (1 - factor) + color2[2] * factor)
                    a = int(color1[3] * (1 - factor) + color2[3] * factor) if len(color1) > 3 else 255
                    
                    image.putpixel((x, y), (r, g, b, a))
                    
        elif gradient_type == "Radial":
            # Radial gradient from center
            center_x, center_y = width // 2, height // 2
            max_distance = max(width, height) // 2
            
            for y in range(height):
                for x in range(width):
                    distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
                    factor = min(distance / max_distance, 1.0)
                    
                    r = int(color1[0] * (1 - factor) + color2[0] * factor)
                    g = int(color1[1] * (1 - factor) + color2[1] * factor)
                    b = int(color1[2] * (1 - factor) + color2[2] * factor)
                    a = int(color1[3] * (1 - factor) + color2[3] * factor) if len(color1) > 3 else 255
                    
                    image.putpixel((x, y), (r, g, b, a))
                    
        elif gradient_type == "Circular":
            # Circular gradient with angle offset
            import math
            center_x, center_y = width // 2, height // 2
            max_distance = max(width, height) // 2
            
            for y in range(height):
                for x in range(width):
                    # Calculate angle from center
                    dx = x - center_x
                    dy = y - center_y
                    pixel_angle = math.degrees(math.atan2(dy, dx)) + angle
                    pixel_angle = pixel_angle % 360
                    
                    # Use angle as factor
                    factor = pixel_angle / 360
                    
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
                    self.bg_gradient_var.get(), self.bg_gradient_angle_var.get()
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
            
            # Calculate position based on alignment
            alignment = self.alignment_var.get()
            if alignment == "nw":  # Top-left
                x, y = 10, 10
            elif alignment == "n":  # Top-center
                x, y = (width - text_width) // 2, 10
            elif alignment == "ne":  # Top-right
                x, y = width - text_width - 10, 10
            elif alignment == "w":  # Middle-left
                x, y = 10, (height - text_height) // 2
            elif alignment == "center":  # Center
                x, y = (width - text_width) // 2, (height - text_height) // 2
            elif alignment == "e":  # Middle-right
                x, y = width - text_width - 10, (height - text_height) // 2
            elif alignment == "sw":  # Bottom-left
                x, y = 10, height - text_height - 10
            elif alignment == "s":  # Bottom-center
                x, y = (width - text_width) // 2, height - text_height - 10
            elif alignment == "se":  # Bottom-right
                x, y = width - text_width - 10, height - text_height - 10
            else:
                x, y = (width - text_width) // 2, (height - text_height) // 2
            
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
                glow_alpha = int(255 * glow_intensity / 100)
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
                
                # Create gradient for the full image size
                text_gradient = self.create_gradient(
                    (width, height),
                    text_color1 + (255,),
                    text_color2 + (255,),
                    self.text_gradient_var.get(),
                    self.text_gradient_angle_var.get()
                )
                
                # Apply the text mask to the gradient
                text_gradient.putalpha(text_mask)
                
                # Composite the gradient text
                main_text_layer = Image.alpha_composite(main_text_layer, text_gradient)
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
                    'bg_opacity': self.bg_opacity_var.get(),
                    'bg_color': self.bg_color_var.get(),
                    'bg_color2': self.bg_color2_var.get(),
                    'bg_gradient': self.bg_gradient_var.get(),
                    'bg_gradient_angle': self.bg_gradient_angle_var.get(),
                    'image_width': self.image_width_var.get(),
                    'image_height': self.image_height_var.get(),
                    'alignment': self.alignment_var.get()
                }
                
                with open(file_path, 'w') as f:
                    json.dump(preset_data, f, indent=2)
                
                messagebox.showinfo("Success", f"Preset saved as {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save preset: {str(e)}")
    
    def load_preset(self):
        """Load settings from a preset"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir="presets"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    preset_data = json.load(f)
                
                # Apply settings
                self.text_var.set(preset_data.get('text', 'Sample Text'))
                self.font_size_var.set(preset_data.get('font_size', 48))
                self.font_var.set(preset_data.get('font', ''))
                self.text_color_var.set(preset_data.get('text_color', '#000000'))
                self.text_color2_var.set(preset_data.get('text_color2', '#FFFFFF'))
                self.text_outline_color_var.set(preset_data.get('text_outline_color', '#FFFFFF'))
                self.text_glow_color_var.set(preset_data.get('text_glow_color', '#0000FF'))
                self.glow_intensity_var.set(preset_data.get('glow_intensity', 50))
                self.glow_radius_var.set(preset_data.get('glow_radius', 3))
                self.glow_enabled_var.set(preset_data.get('glow_enabled', True))
                self.outline_thickness_var.set(preset_data.get('outline_thickness', 2))
                self.text_gradient_var.set(preset_data.get('text_gradient', 'None'))
                self.text_gradient_angle_var.set(preset_data.get('text_gradient_angle', 0))
                self.bg_opacity_var.set(preset_data.get('bg_opacity', preset_data.get('bg_transparency', 100)))  # backward compatibility
                self.bg_color_var.set(preset_data.get('bg_color', '#FFFFFF'))
                self.bg_color2_var.set(preset_data.get('bg_color2', '#000000'))
                self.bg_gradient_var.set(preset_data.get('bg_gradient', 'None'))
                self.bg_gradient_angle_var.set(preset_data.get('bg_gradient_angle', 0))
                self.image_width_var.set(preset_data.get('image_width', 800))
                self.image_height_var.set(preset_data.get('image_height', 400))
                self.alignment_var.set(preset_data.get('alignment', 'center'))
                
                # Update color buttons and preview
                self.update_color_buttons()
                self.update_preview()
                
                messagebox.showinfo("Success", f"Preset loaded from {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load preset: {str(e)}")

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
