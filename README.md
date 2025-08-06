# Font Image Maker

A powerful desktop application that converts text into beautiful, customizable images with extensive styling options including gradients, glows, outlines, and custom fonts.

## Features

### Text Styling
- **Typography**: Choose from system fonts or upload custom .ttf/.otf fonts
- **Size Control**: Adjustable font size (8-200pt) with live preview
- **Color Options**: Solid colors or gradients (Linear, Radial, Circular)
- **Text Effects**: 
   - Customizable outline with thickness control (0-10px)
   - Glow effects with intensity and radius controls
   - Multiple gradient types with angle adjustment (0-360°)

### Background Control
- **Transparency**: Adjustable opacity (0-100%) for overlay effects
- **Colors**: Solid or gradient backgrounds
- **Gradient Support**: Linear, Radial, and Circular gradients
- **Custom Sizing**: Set exact image dimensions in pixels

### Layout & Alignment
- **Smart Alignment**: 9-point grid system for precise text positioning
- **Custom Canvas**: Define exact image dimensions
- **Real-time Preview**: See changes instantly as you design

### Export & Sharing
- **Multiple Formats**: Save as PNG, JPEG, BMP, or TIFF
- **Clipboard Support**: Copy images directly for pasting
- **Preset System**: Save and load styling configurations

## Quick Start

### Easy Launch (Windows)
- **Double-click** `run_app.bat` for automatic setup
- **Right-click** `run_app.ps1` → "Run with PowerShell"

### Manual Installation
1. Ensure Python 3.7+ is installed
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Launch the application:
    ```bash
    python font_image_maker.py
    ```

## Usage Guide

### Basic Workflow
1. **Enter Text**: Type your message in the text input field
2. **Style Your Text**: 
    - Choose colors using the color picker buttons
    - Select fonts from the dropdown or upload custom ones
    - Adjust size, outline, and glow effects
3. **Customize Background**: Set colors, gradients, and transparency
4. **Position Text**: Use the 3×3 alignment grid
5. **Preview & Export**: Watch live preview and save when satisfied

### Pro Tips
- **Professional Look**: Use subtle outlines (1-2px) and low glow intensity
- **Eye-catching Design**: Try gradient backgrounds with contrasting text
- **Custom Fonts**: Upload .ttf or .otf files for unique typography
- **Presets**: Save your favorite styles for quick reuse

## Project Structure

```
Font Image Maker/
├── font_image_maker.py         # Main application
├── requirements.txt            # Python dependencies
├── run_app.bat                # Windows launcher (batch)
├── run_app.ps1                # Windows launcher (PowerShell)
├── README.md                  # Project documentation
├── QUICKSTART.md              # Quick start guide
├── HELP.md                    # Detailed help documentation
├── fonts/                     # Custom fonts storage
├── presets/                   # Saved styling presets
│   ├── professional_preset.json
│   └── vibrant_preset.json
└── __pycache__/              # Python cache files
```

## System Requirements

- **Python**: 3.7 or higher
- **Operating System**: Windows, macOS, or Linux
- **Dependencies**: See `requirements.txt`
- **Note**: tkinter is included with most Python installations

## Supported Formats

### Input Files
- **Fonts**: .ttf, .otf (TrueType and OpenType fonts)
- **Presets**: .json (styling configuration files)

### Output Files
- **Images**: .png, .jpg, .jpeg, .bmp, .tiff
- **Clipboard**: PNG format for direct pasting

## Troubleshooting

### Common Issues

**"tkinter not found" Error**
- **Windows**: Reinstall Python with "tcl/tk and IDLE" option checked
- **Ubuntu/Debian**: `sudo apt-get install python3-tk`
- **CentOS/RHEL**: `sudo yum install tkinter`

**Font Upload Issues**
- Ensure font files are .ttf or .otf format
- Check file permissions in the `fonts/` directory
- Try restarting the application after font installation

**Performance Issues**
- Reduce glow radius and intensity for better performance
- Use smaller image dimensions for faster rendering
- Close other applications to free up memory

**Launcher Problems**
- Try running `python font_image_maker.py` directly
- Check Python installation: `python --version`
- Manually install Pillow: `pip install Pillow>=8.0.0`

## Contributing

This is an open-source project. Feel free to:
- Report bugs and issues
- Suggest new features
- Submit improvements
- Share your presets

## License

This project is open source. See the project repository for license details.

---

**Need help?** Check out `QUICKSTART.md` for a quick tutorial or `HELP.md` for detailed documentation.

1. **Font not loading**: Ensure font file is valid .ttf or .otf format
2. **Preview not updating**: Check that all required fields are filled
3. **Export fails**: Verify write permissions in the output directory
4. **Colors not displaying**: Ensure RGB values are between 0-255

### System Requirements
- Windows 7+ / macOS 10.9+ / Linux with GUI
- Minimum 4GB RAM recommended
- 100MB free disk space

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the application.
