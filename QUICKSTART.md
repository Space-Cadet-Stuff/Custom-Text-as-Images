# Quick Start Guide

Get started with Font Image Maker in just a few minutes!

## Installation & Launch

### Windows Users (Recommended)
**Option 1: One-Click Launch**
- Double-click `run_app.bat` in the project folder
- The launcher will automatically install dependencies and start the app

**Option 2: PowerShell Launch**
- Right-click `run_app.ps1` → "Run with PowerShell"
- Allows for better error handling and progress display

### Manual Launch (All Platforms)
1. Open terminal/command prompt in the project folder
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Run the application:
    ```bash
    python font_image_maker.py
    ```

## Create Your First Image

### Step 1: Enter Your Text
- Type your message in the **"Text"** field at the top
- See it appear instantly in the preview area

### Step 2: Choose Your Style
- **Font**: Select from a font or click "Upload Font" for custom fonts
- **Size**: Use the spinner control (8-200pt)
- **Colors**: Click color buttons to open the color picker
- **Effects**: Try outline thickness and glow settings

### Step 3: Perfect the Background
- **Transparency**: Adjust the percentage for overlay effects
- **Colors**: Set solid colors or create gradients
- **Size**: Set custom image dimensions in pixels

### Step 4: Position & Align
- Use the **3×3 alignment grid** to position your text:
  ```
  ┌─────┬─────┬─────┐
  │ TL  │ TC  │ TR  │ ← Top Row
  ├─────┼─────┼─────┤
  │ ML  │ MC  │ MR  │ ← Middle Row
  ├─────┼─────┼─────┤
  │ BL  │ BC  │ BR  │ ← Bottom Row
  └─────┴─────┴─────┘
  ```

### Step 5: Export Your Creation
- **Save Image**: Choose format (PNG recommended for transparency)
- **Copy to Clipboard**: Perfect for pasting into other applications

## Styling Quick Reference

### Professional Look
```
✓ Dark text on light background
✓ Subtle outline (1-2px thickness)
✓ Low glow intensity (20-30%)
✓ Solid colors or subtle gradients
✓ Center or left alignment
```

### Eye-Catching Design
```
✓ Bright gradient backgrounds
✓ High glow intensity (60-80%)
✓ Larger glow radius (10-15px)
✓ Contrasting color combinations
✓ Thick outlines (3-5px) for bold text
```

### Logo/Branding Style
```
✓ Custom fonts (.ttf/.otf uploads)
✓ Consistent color schemes
✓ Transparent backgrounds
✓ Precise alignment
✓ Save as preset for reuse
```

## Essential Controls Reference

| Control | Location | Purpose | Tip |
|---------|----------|---------|-----|
| **Text Input** | Top of left panel | Enter your message | Live preview updates as you type |
| **Font Dropdown** | Text section | Choose typeface | Upload custom fonts for more options |
| **Size Spinner** | Text section | Adjust font size (8-200pt) | Use larger sizes for better glow effects |
| **Color Buttons** | Throughout interface | Open color picker | RGB values update automatically |
| **Gradient Type** | Text & Background | Select gradient style | Try "Circular" for dramatic effects |
| **Alignment Grid** | General section | Position text in image | Click buttons to see instant positioning |
| **Transparency Slider** | Background section | Control background opacity | 0% = transparent, 100% = solid |
| **Outline Thickness** | Text effects | Border width around text | Higher values work better with large fonts |
| **Glow Controls** | Text effects | Create lighting effects | Combine intensity + radius for best results |

## Included Presets

### `professional_preset.json`
- Clean, business-appropriate styling
- Subtle effects and neutral colors
- Perfect for presentations and documents

### `vibrant_preset.json`
- Bold, colorful design
- Strong glow and gradient effects
- Great for social media and gaming

### `vaporwave_preset.json`
- 80s inspired design
- Synthy vibes
- Bit more niche but I love it

**Load presets by clicking "Load Preset" and selecting the .json file**

## Pro Tips

- **Performance**: Lower glow settings render faster
- **Quality**: Use PNG format to preserve transparency
- **Fonts**: Uploaded fonts are permanently saved in `fonts/` folder
- **Presets**: Save your favorite styles for quick reuse
- **Alignment**: Preview updates instantly when clicking alignment buttons
- **Colors**: Try gradients with complementary colors for best results

---

**Next Steps**: 
- Read `HELP.md` for detailed feature explanations
- Experiment with different font and color combinations
- Create and save your own preset styles!
| Font Size | Below text | Adjust size with slider (8-200pt) |
| Colors | Color buttons | Click to choose colors |
| Glow Controls | Below colors | Adjust intensity (%) and radius (px) |
| Outline Thickness | Below glow | Adjust outline width (0-10px) |
| Opacity | Background section | Control transparency (0-100%) |
| Alignment | 3×3 grid | Position your text |
| Save Image | Bottom buttons | Export your creation |

## File Structure
```
Font Image Maker/
├── font_image_maker.py     ← Main app
├── run_app.bat            ← Windows launcher
├── fonts/                 ← Your custom fonts
├── presets/              ← Saved settings
└── README.md             ← Full documentation
```

## Need Help?
- Read `HELP.md` for detailed instructions
- Check `README.md` for technical details

## Common Tasks

**Add Custom Font:**
1. Click "Upload Font"
2. Select .ttf or .otf file
3. Font appears in dropdown

**Save Your Settings:**
1. Configure everything you like
2. Click "Save Preset"
3. Name and save your .json file

**Change Image Size:**
1. Find "Image Size" in General Settings
2. Enter width × height in pixels
3. Preview updates automatically

**Make Transparent Background:**
1. Set "Opacity" to 0%
2. Save as PNG format (not JPEG)

**Create Dramatic Glow:**
1. Increase "Glow Intensity" to 80-100%
2. Set "Glow Radius" to 8-15px
3. Choose a bright glow color

**Add Bold Outline:**
1. Set "Outline Thickness" to 4-6px
2. Choose contrasting outline color

---
**Ready to create amazing text images? Launch the app and start designing!**
