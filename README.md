# CopyPasteBasedEmojiRemover

A lightweight Windows utility that automatically removes emojis from clipboard text before pasting.

## Features

* Automatically strips emojis when using **Ctrl+V**
* Preserves normal text formatting
* Configurable through a simple JSON configuration file
* System tray integration
* Single-instance protection (prevents multiple copies from running)
* Lightweight and runs in the background
* No manual interaction required during normal use

## How It Works

When you press **Ctrl+V**, the application:

1. Reads the current clipboard text.
2. Removes emoji characters according to the configured rules.
3. Replaces the clipboard content with the cleaned text.
4. Pastes the cleaned text into the active application.

If no emojis are detected, the original text is pasted unchanged.

## Requirements

* Windows
* Python 3.8+
* Administrator privileges recommended for reliable global hotkey interception

## Installation

Install the required dependencies:

```bash
pip install keyboard pyperclip pystray pillow
```

## Running

```bash
python main.py
```

The application will start in the background and place an icon in the system tray.

## Configuration

Configuration is stored in:

```text
%APPDATA%\CopyPasteBasedEmojiRemover\config.json
```

Default configuration:

```json
{
    "remove_emojis": true
}
```

### Available Options

| Option        | Description                               |
| ------------- | ----------------------------------------- |
| remove_emojis | Removes emoji characters from pasted text |

## Hotkeys

| Hotkey   | Action                  |
| -------- | ----------------------- |
| Ctrl + V | Remove emojis and paste |

## Example

Input:

```text
Hello  World 
```

Output:

```text
Hello  World
```

## Notes

* Works only with text currently stored in the clipboard.
* Non-text clipboard content is ignored.
* Running as Administrator may improve compatibility with certain applications.
* Only one instance of the application can run at a time.

## Troubleshooting

### Ctrl+V does not work

Try running the application as Administrator.

### Another instance is already running

Only one instance can be active at a time. Close the existing instance before launching another.

### Emojis are not being removed

Verify that:

* `remove_emojis` is set to `true`
* The application is running
* The clipboard contains text data
