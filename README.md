# 🎬 Motion Design Project Creator

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)](https://pypi.org/project/PyQt5/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()

> **Professional project structure generator for motion designers and video creators**

A smart desktop application that automatically creates organized folder structures for motion design projects with support for multiple industry-standard tools.

## ✨ Features

### 🎯 **Smart Project Organization**
- **Standardized Structure**: Creates industry-standard folder hierarchy
- **Multi-Tool Support**: After Effects, Cinema 4D, Premiere Pro, Houdini, Blender
- **Template Integration**: Includes pre-configured project templates
- **Adaptive Interface**: Responsive UI that scales to different screen sizes

### 🛠️ **Professional Workflow**
- **Customizable Structure**: Modify folder structure to match your workflow
- **Quick Setup**: Create complete project in seconds
- **Path Management**: Remember favorite project locations
- **Bilingual Support**: Russian and English interface

### 📁 **Generated Structure**
```
📁 [Project Name]/
├── 📁 01_IN/               # Source materials
│   ├── 📁 FOOTAGES/        # Video files
│   ├── 📁 SFX/             # Audio & music
│   ├── 📁 FONTS/           # Typography
│   └── 📁 ASSETS/          # Graphics & textures
├── 📁 02_PROCESS/          # Working files
│   ├── 📁 AE/              # After Effects projects
│   ├── 📁 C4D/             # Cinema 4D scenes
│   ├── 📁 PR/              # Premiere Pro projects
│   ├── 📁 HOUDINI/         # Houdini files
│   └── 📁 BLENDER/         # Blender projects
├── 📁 03_RENDER/           # Render output
└── 📁 04_OUT/              # Final deliverables
    ├── 📁 01_PREVIEW/      # Client previews
    ├── 📁 02_STILLSHOTS/   # Still frames
    ├── 📁 03_ANIMATIC/     # Storyboards
    └── 📁 04_MASTER/       # Final files
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- PyQt5

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/RemitOtkin/Motion_Design_Project_Creator.git
   cd Motion_Design_Project_Creator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   launch.bat
   ```

## 🔧 Configuration

### Customizing Folder Structure
The application allows you to:
- Modify default folder names and hierarchy
- Create and save custom templates
- Add comments to folders for team clarity
- Include/exclude specific tool folders

### Settings
- **Default Project Path**: Set your preferred projects directory
- **Language**: Switch between Russian and English
- **Window Preferences**: Automatic geometry saving

## 🏗️ Architecture

### Core Components
- **`core/project_creator.py`** - Main project creation logic
- **`core/folder_structure_manager.py`** - Structure management and templates
- **`ui/main_window.py`** - Primary application interface
- **`ui/components/`** - Reusable UI components
- **`config/`** - Settings and translations

### Key Features
- **Threaded Operations**: Non-blocking project creation
- **Adaptive UI**: Screen-aware interface scaling
- **Cross-Platform**: Windows, macOS, and Linux support
- **Extensible**: Easy to add new tools and templates

## 🎨 For Motion Designers

### Supported Workflows
- **Commercial Projects**: Client work organization
- **Personal Projects**: Creative experiments
- **Team Collaboration**: Standardized structure for teams
- **Asset Management**: Organized resource storage

### Industry Integration
- Pre-configured templates for major motion design tools
- Follows industry naming conventions
- Compatible with asset management workflows
- Supports render farm organization

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request


### Version 1.0
- [x] Basic project structure creation
- [x] Multi-tool support
- [x] Customizable folder structure
- [x] Bilingual interface

### Version 1.1 (Planned)
- [ ] Project templates library
- [ ] Asset preview integration
- [ ] Cloud sync capabilities
- [ ] Team collaboration features

## 🐛 Known Issues

- Animation button hover effects may cause UI lag on some systems
- Large project structures (>1000 folders) may take time to generate
- Some antivirus software may flag the executable (false positive)

## 💡 Tips & Best Practices

### For Teams
1. **Standardize Templates**: Use consistent folder structures across projects
2. **Asset Naming**: Follow clear naming conventions
3. **Version Control**: Keep template files in version control
4. **Documentation**: Use README files in project folders

### For Freelancers
1. **Client Organization**: Create separate root folders for different clients
2. **Archive Strategy**: Move completed projects to archive folders
3. **Backup Planning**: Ensure render and source folders are backed up
4. **Asset Reuse**: Maintain a library of reusable assets

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Remit Otkin**
- GitHub: [@RemitOtkin](https://github.com/RemitOtkin)
- Email: [your-email@example.com]

## 🙏 Acknowledgments

- PyQt5 team for the excellent GUI framework
- Motion design community for workflow insights
- Beta testers and early adopters


---

<div align="center">
<strong>⭐ Star this project if it helps you organize your motion design workflow! ⭐</strong>
</div>