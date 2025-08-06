# Font Image Maker - Help Guide

## Getting Started

### First Time Setup
1. Make sure Python 3.7+ is installed on your system
2. Double-click `run_app.bat` (Windows) or `run_app.ps1` (PowerShell) to start the application
3. The launcher will automatically install required dependencies

### Manual Installation
If the automatic launcher doesn't work:
```bash
pip install Pillow
python font_image_maker.py
```

## User Interface Guide

### Left Panel - Controls

#### Text Settings
- **Text**: Enter the text you want to convert to an image
- **Size (pt)**: Font size in points (8-200)
- **Font**: Select from available system fonts or uploaded custom fonts
- **Upload Font**: Add custom .ttf or .otf font files
- **Text Color**: Primary text color (click to open color picker)
- **Secondary Color**: Second color for gradients
- **Outline Color**: Color for text outline effect
- **Glow Color**: Color for text glow effect
- **Gradient Type**: None, Linear, Radial, or Circular gradients
- **Gradient Angle**: Direction of linear gradients (0-360°)

#### Background Settings
- **Transparency (%)**: Background opacity (0% = transparent, 100% = opaque)
- **BG Color**: Primary background color
- **BG Secondary**: Second background color for gradients
- **BG Gradient**: Background gradient type
- **BG Angle**: Background gradient direction

#### General Settings
- **Image Size**: Width × Height in pixels
- **Text Alignment**: 9-position grid for text placement
  - Top: Left, Center, Right
  - Middle: Left, Center, Right  
  - Bottom: Left, Center, Right

### Right Panel - Preview
- **Live Preview**: Shows your text image in real-time
- **Scroll**: Use scrollbars if image is larger than preview area
- **Zoom**: Preview automatically scales to fit while maintaining aspect ratio

### Bottom Panel - Actions
- **Save Image**: Export as PNG, JPEG, BMP, or TIFF
- **Copy to Clipboard**: Copy image for pasting into other applications
- **Save Preset**: Save current settings as a .json preset file
- **Load Preset**: Load previously saved settings

## Features Explained

### Text Effects

#### Outline
Creates a border around text characters. Useful for making text stand out against backgrounds.

#### Glow
Adds a soft glowing effect around text. Creates a subtle shadow/halo effect.

#### Gradients
- **None**: Solid color
- **Linear**: Color transition in a straight line
- **Radial**: Color transition from center outward
- **Circular**: Circular color transition

### Background Options

#### Transparency
- 0%: Completely transparent background
- 50%: Semi-transparent background
- 100%: Solid background

#### Gradients
Same options as text gradients, applied to the entire background.

### Font Management

#### System Fonts
The application includes common system fonts like Arial, Times New Roman, etc.

#### Custom Fonts
1. Click "Upload Font" button
2. Select a .ttf or .otf font file
3. Font is copied to the `fonts/` folder
4. Font appears in the dropdown list
5. Select and use like any system font

#### Supported Font Formats
- **TrueType Fonts (.ttf)**: Most common format
- **OpenType Fonts (.otf)**: Advanced font format with more features

### Preset System

#### Saving Presets
1. Configure your text and background settings
2. Click "Save Preset"
3. Choose a filename and location (default: `presets/` folder)
4. Settings saved as .json file

#### Loading Presets
1. Click "Load Preset"
2. Select a .json preset file
3. All settings are applied automatically
4. Preview updates immediately

#### Included Presets
- **vibrant_preset.json**: Colorful design with gradients
- **professional_preset.json**: Clean, business-appropriate style

### Export Options

#### Image Formats
- **PNG**: Best for text with transparency, lossless quality
- **JPEG**: Smaller file size, good for photos, no transparency
- **BMP**: Windows bitmap format
- **TIFF**: High-quality format for professional use

#### Clipboard Copy
- Windows: Uses system clipboard for direct pasting
- Other platforms: Manual save recommended

## Tips and Best Practices

### Text Readability
- Use high contrast between text and background colors
- Add outline or glow for text over complex backgrounds
- Choose appropriate font sizes for your image resolution

### File Organization
- Keep custom fonts in the `fonts/` folder
- Save frequently used settings as presets
- Use descriptive names for saved images and presets

### Performance
- Large images (>2000px) may take longer to preview
- Complex gradients can slow down real-time preview
- Close and reopen the application if preview becomes sluggish

### Color Selection
- Click any color button to open the color picker
- RGB values are automatically calculated
- Hex codes are displayed for web use
- Use similar colors for subtle gradients
- Use contrasting colors for dramatic effects

## Troubleshooting

### Common Issues

#### "No module named PIL"
Solution: Install Pillow package
```bash
pip install Pillow
```

#### Font not appearing in list
- Verify font file is .ttf or .otf format
- Check that file copied to `fonts/` folder
- Restart application to refresh font list

#### Preview not updating
- Check all required fields are filled
- Try changing text or size to trigger update
- Restart application if issue persists

#### Export fails
- Verify you have write permissions to the destination folder
- Check that filename doesn't contain invalid characters
- Try saving to a different location

#### Clipboard copy doesn't work
- Windows users: Try installing pywin32 package
- Alternative: Save image and manually copy
- Some applications may not accept clipboard images

### Error Messages

#### "Failed to load font"
- Font file may be corrupted
- Try a different font file
- Check font file format (.ttf or .otf)

#### "Image too large"
- Reduce image dimensions
- Maximum recommended: 5000×5000 pixels
- Large images use more memory

#### "Cannot save image"
- Check file permissions
- Verify destination folder exists
- Try a different file format

## Advanced Usage

### Command Line
You can also run the application from command line:
```bash
cd "Font Image Maker"
python font_image_maker.py
```

### Customizing the Application
The application is open source. You can modify:
- `font_image_maker.py`: Main application logic
- Add new gradient types or effects
- Modify the user interface layout
- Add new export formats

### Batch Processing
For multiple images with same settings:
1. Configure your desired settings
2. Save as a preset
3. Change only the text for each image
4. Export each variation

## Support

For issues or questions:
1. Check this help guide first
2. Verify all dependencies are installed
3. Try the included sample presets
4. Run `test_dependencies.py` to check your setup

## Version Information
- **Python**: 3.7+ required
- **Pillow**: 8.0.0+ recommended
- **tkinter**: Included with Python
- **Platform**: Windows, macOS, Linux
