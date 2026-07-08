# ⚡ Phasor Diagram Tool

A professional-grade desktop application for constructing and analysing **phasor diagrams** used in AC circuit analysis. Built with Python, Tkinter, and Matplotlib.

---

## ✨ Features

### Core
- **Unlimited phasors** — add as many phasors as needed with magnitude (float) and angle (degrees)
- **Per-phasor line styles** — Solid, Dotted, or Dashed lines for each phasor independently
- **Custom start points** — draw phasors from the **Origin** or from the **tip of any other phasor** (tip-to-tail) to form voltage/impedance/power triangles
- **Full colour customisation** — pick colours for each phasor and for diagram elements (background, grid, axes, labels)

### Diagram
- Polar grid with concentric circles and 30° radial lines
- Angle arcs with degree labels
- Axis projections (Real/Imaginary components)
- Component value display (polar notation on labels)
- Anti-overlap label collision avoidance algorithm with leader lines

### Editing
- **Click any row** in the phasor table to select and edit its values
- Arrow key (↑/↓) navigation between input fields
- Enter key to submit from any field
- **"+ Add New Phasor"** button at the bottom of the table

### Export
- Save diagrams as **PNG**, **JPEG**, **SVG**, or **PDF**
- High DPI (200) export for publication quality

---

## 📦 Installation

### Prerequisites
- **Python 3.8+**
- **Tkinter** (usually bundled with Python on Windows/macOS)

### Setup

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/phasor-diagram-tool.git
cd phasor-diagram-tool

# Install dependencies
pip install -r requirements.txt
```

### Run

**Option A: Command Line**
```bash
python phasor_diagram.py
```

**Option B: Windows Double-Click**
Double-click `run.bat` in File Explorer to automatically start the application (and install any missing dependencies).

---

## 🖥️ Usage

### Adding Phasors
1. Enter **Label** (auto-generated as E1, E2, …), **Magnitude**, and **Angle** (degrees)
2. Choose **Line Style** (Solid / Dotted / Dashed)
3. Select **Start From** — `Origin` or `Tip of [phasor]` for chained diagrams
4. Pick a **Colour** or use the auto-assigned one
5. Click **Add Phasor** or press **Enter**

### Drawing Triangles (Tip-to-Tail)
1. Add **E1** (e.g., 100 ∠ 0°) — starts from Origin
2. Add **E2** (e.g., 80 ∠ 90°) — set "Start From" to **Tip of E1**
3. Add **E3** — set "Start From" to **Tip of E2**
4. The three phasors form a closed triangle

### Editing Phasors
- **Click a row** in the Phasor Table → values load into the input form
- Modify and click **Update Phasor**
- Click **"+ Add New Phasor"** to switch back to add mode

### Toolbar Toggles
| Toggle | Description |
|--------|-------------|
| Grid | Show/hide polar grid |
| Labels | Show/hide phasor labels |
| Arcs | Show/hide angle arcs |
| Projections | Show/hide Re/Im projections |

### Keyboard Shortcuts
| Key | Action |
|-----|--------|
| `↑` / `↓` | Navigate between input fields |
| `Enter` | Add/Update phasor |
| `Tab` / `Shift+Tab` | Cycle input fields |
| `Ctrl+S` | Save diagram image |

---

## 📁 Project Structure

```
phasor-diagram-tool/
├── phasor_diagram.py    # Main GUI application (single-file)
├── run.bat              # One-click Windows launcher
├── requirements.txt     # Python dependencies (numpy, matplotlib)
├── LICENSE              # MIT License
├── .gitignore           # Git ignore rules
└── README.md            # Documentation
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| GUI Framework | Tkinter + ttk |
| Plotting | Matplotlib (TkAgg backend) |
| Math | NumPy |
| Language | Python 3.8+ |

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request
