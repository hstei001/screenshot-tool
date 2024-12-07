# Python Screenshot App

A simple screenshot application built with PyQt6.

## Features
- Capture full screen screenshots
- Save screenshots with custom file names
- Modern, minimal interface
- Draggable window
- Always-on-top functionality

## Installation

1. Make sure you have Python 3.8+ installed
2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Running the App
```bash
python screenshot_app.py
```

## Usage
1. Click the "Capture Screenshot" button to take a screenshot
2. Choose where to save your screenshot in the file dialog
3. Drag the window by clicking and holding anywhere on the toolbar
4. Click the X button to close the app

## Antivirus Warning

Some antivirus software might flag this application as suspicious. This is a **false positive** due to how Python applications are packaged into standalone executables. The application is completely safe to use, and here's why:

1. The source code is open source and available for inspection in this repository
2. The executable is built using PyInstaller, a standard tool for packaging Python applications
3. The application has been signed with proper metadata and version information
4. You can always build the executable yourself from the source code if you prefer

If your antivirus software flags the application:
1. You can safely add it to your antivirus exceptions
2. Alternatively, you can clone this repository and build it yourself using the instructions below
