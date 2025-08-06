# Font Image Maker

A desktop application that converts text to customizable images with extensive styling options.

## Features

### Text Customization
- **Text Outline Color**: RGB color picker for text outline
- **Outline Thickness**: Adjustable thickness slider (0-10px)
- **Text Glow**: RGB color picker with customizable glow effect
- **Glow Intensity**: Adjustable intensity slider (0-100%)
- **Glow Radius**: Adjustable radius slider (0-20px)
- **Text Color(s)**: RGB color picker with gradient support
- **Gradient Types**: None, Linear, Radial, Circular
- **Gradient Angle**: Adjustable slider (0-360°) with degree display
- **Font Selection**: Choose from system fonts or upload custom fonts
- **Font Size**: Adjustable slider (8-200pt) with point display

### Background Customization
- **Opacity**: Adjustable percentage slider (0-100%) with percentage display
- **Background Color(s)**: RGB color picker with gradient support
- **Gradient Types**: None, Linear, Radial, Circular
- **Gradient Angle**: Adjustable slider (0-360°) with degree display

### General Settings
- **Text Alignment**: 9-point alignment system (Top-Left, Top-Center, Top-Right, Middle-Left, Center, Middle-Right, Bottom-Left, Bottom-Center, Bottom-Right)
- **Text Size**: Adjustable slider in points (8-200pt) with live display
- **Image Size**: Custom width and height in pixels

### Additional Features
- **Font Management**: Upload and store custom fonts (.ttf, .otf)
- **Export Options**: Save as PNG/JPEG or copy to clipboard
- **Real-time Preview**: Live preview of text styling
- **Preset Management**: Save and load styling presets

## Requirements

- Python 3.7+
- tkinter (usually included with Python)
- Pillow (PIL) for image processing
- tkinter.colorchooser for color selection

## Installation

1. Clone or download this repository
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python font_image_maker.py
   ```

## Usage

1. **Enter Text**: Type your desired text in the text input field
2. **Customize Appearance**: Use the various controls to style your text and background
3. **Preview**: See real-time changes in the preview area
4. **Export**: Save your image or copy to clipboard

### Font Management
- Click "Upload Font" to add custom .ttf or .otf font files
- Uploaded fonts are stored in the `fonts/` directory
- Custom fonts appear in the font dropdown after upload

### Color Selection
- Click any color button to open the color picker
- RGB values are displayed and can be manually entered
- Gradient colors can be set using the primary and secondary color options

### Alignment Options
- Use the 3x3 grid of alignment buttons to position text
- Options include all combinations of Top/Middle/Bottom and Left/Center/Right

## File Structure

```
Font Image Maker/
├── font_image_maker.py     # Main application file
├── requirements.txt        # Python dependencies
├── fonts/                  # Custom fonts directory
├── presets/               # Saved styling presets
└── README.md              # This file
```

## Supported File Formats

### Input
- **Fonts**: .ttf, .otf
- **Presets**: .json

### Output
- **Images**: .png, .jpg, .jpeg, .bmp, .tiff
- **Clipboard**: PNG format

## Troubleshooting

### Common Issues

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
