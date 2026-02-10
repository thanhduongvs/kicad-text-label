# Text Label Generator

A powerful **KiCad 9.0+** plugin for generating high-quality, vector-based text labels and symbols directly on your PCB. 

This tool allows you to use TrueType fonts, create inverted (negative) text, apply custom border styles, and mix multiple fonts in a single label using a rich-text tagging system.

![Preview Screenshot](https://raw.githubusercontent.com/thanhduongvs/kicad-text-label/main/docs/preview.png)
*(Replace this link with an actual screenshot of your UI)*

## ✨ Features

* **TrueType/OpenType Support:** Load and render any `.ttf` or `.otf` font.
* **Rich Text Tagging:** Mix different fonts in one string (e.g., `{Roboto}Text {FontAwesome}Icon{/FontAwesome}{/Roboto}`).
* **Negative Rendering:** Easily create "inverted" text (text cut out from a solid block) for silkscreen or copper layers.
* **Advanced Geometry Processing:** * Robust boolean operations for complex fonts (like Roboto) to prevent self-intersection artifacts.
    * Optimized path stitching for symbol fonts.
* **Custom Borders & Caps:**
    * Styles: Square, Round, Triangle, Pointed, Ribbon (In/Out), Trapezoid.
    * Adjustable border width and corner radius.
* **Symbol Picker:** Built-in visual dialog to browse and select icons from loaded symbol fonts.
* **Live Preview:** Real-time WYSIWYG preview with auto-zoom and pan.
* **Export Options:**
    * **Copy to Clipboard:** Paste directly into Pcbnew.
    * **Save as File:** Save as a `.kicad_mod` footprint file.

## 🚀 Installation

### Via KiCad Plugin and Content Manager (Recommended)
1.  Open KiCad.
2.  Go to **Plugin and Content Manager (PCM)**.
3.  Search for "Text Label Generator".
4.  Click **Install**.

### Manual Installation
1.  Download the latest release `.zip` from the [Releases page](../../releases).
2.  Open KiCad -> **Plugin and Content Manager**.
3.  Click **Install from File...** and select the downloaded zip.

## 🛠 Usage

1.  **Open the Plugin:** Click the "Text Label Generator" icon in the PCB Editor toolbar.
2.  **Select Font:** Choose a text font or a symbol font from the dropdown.
3.  **Input Text:** * Type your text in the input box.
    * Changing fonts automatically inserts tags (e.g., `{Arial}My Text{/Arial}`).
    * Click **"Pick Icon"** to visually select symbols from icon fonts.
4.  **Customize Style:**
    * **Layer:** Select target layer (F.SilkS, F.Cu, F.Mask, etc.).
    * **Geometry:** Adjust Height, Spacing, and Border settings.
    * **Effects:** Check **"Negative"** for inverted text or **"No Frame"** for text only.
5.  **Export:**
    * Click **"Copy to Clipboard"** and press `Ctrl+V` in the PCB Editor.
    * Or click **"Save .kicad_mod"** to save it to your library.

## 📂 Font Management
* Place your text fonts in: `plugin_folder/fonts/texts/`
* Place your symbol/icon fonts in: `plugin_folder/fonts/symbols/`

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
**Author:** [Thanh Duong](https://github.com/thanhduongvs)