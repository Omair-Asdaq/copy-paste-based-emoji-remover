import keyboard
import pyperclip
import json
import os
import sys
import time
import re
import threading
import tkinter as tk
import socket
from pathlib import Path

CONFIG_PATH = Path(os.getenv('APPDATA', '~')) / 'CopyPasteBasedEmojiRemover' / 'config.json'
_history = []
_stack = []
_is_processing = False

def load_rules():
    default_rules = {
        "remove_emojis": True
    }
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, 'r') as f:
                return json.load(f)
        except:
            return default_rules
    else:
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, 'w') as f:
            json.dump(default_rules, f, indent=4)
        return default_rules

def transform(text, rules):
    if rules.get("remove_emojis", False):
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"
            u"\U0001F300-\U0001F5FF"
            u"\U0001F680-\U0001F6FF"
            u"\U0001F700-\U0001F77F"
            u"\U0001F780-\U0001F7FF"
            u"\U0001F800-\U0001F8FF"
            u"\U0001F900-\U0001F9FF"
            u"\U0001FA00-\U0001FA6F"
            u"\U0001FA70-\U0001FAFF"
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        text = emoji_pattern.sub(r'', text)
    return text

def add_to_history(text):
    global _history
    if not text or not isinstance(text, str) or len(text.strip()) == 0:
        return
    if text in _history:
        _history.remove(text)
    _history.insert(0, text)
    _history = _history[:5]

def on_copy():
    text = pyperclip.paste()
    add_to_history(text)

def copy_to_stack():
    global _stack
    text = pyperclip.paste()
    if text and isinstance(text, str) and len(text.strip()) > 0:
        _stack.append(text)
        print(f" Stacked: '{text[:30]}...' (Total: {len(_stack)})")
    else:
        print(" Nothing stacked (empty or non-text)")

def on_paste():
    global _is_processing, _stack

    if _is_processing:
        return

    try:
        _is_processing = True

        if _stack:
            combined = "\n".join(_stack)
            pyperclip.copy(combined)
            _stack.clear()
            print(f" Stack flushed ({len(combined)} chars). Stack cleared.")
            time.sleep(0.02)

        original = pyperclip.paste()
        print(f" Original: '{original[:50]}...'")

        if not isinstance(original, str) or len(original.strip()) == 0:
            print("⏭ Skipped (empty or non-text)")
            return

        rules = load_rules()
        new_text = transform(original, rules)

        if new_text != original:
            pyperclip.copy(new_text)
            print(f" Transformed: '{new_text[:50]}...'")
            time.sleep(0.02)
            keyboard.send('ctrl+v')
        else:
            print("ℹ Unchanged (no transform needed)")
            keyboard.send('ctrl+v')

    except Exception as e:
        print(f" Error: {e}")
    finally:
        _is_processing = False

def show_history():
    if not _history:
        print(" History is empty.")
        return

    window = tk.Tk()
    window.title("Last 5 Copies")
    window.geometry("400x250")
    window.attributes('-topmost', True)

    listbox = tk.Listbox(window, font=("Arial", 11))
    listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    for item in _history:
        display = item.replace("\n", " ").strip()[:60]
        listbox.insert(tk.END, display)

    def on_select(event):
        selection = listbox.curselection()
        if selection:
            index = selection[0]
            text = _history[index]
            pyperclip.copy(text)
            window.destroy()
            time.sleep(0.02)
            keyboard.send('ctrl+v')

    listbox.bind('<Double-Button-1>', on_select)
    listbox.bind('<Return>', on_select)

    btn_frame = tk.Frame(window)
    btn_frame.pack(pady=(0, 10))

    tk.Button(btn_frame, text="Paste Selected", command=lambda: on_select(None), width=15).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Cancel", command=window.destroy, width=15).pack(side=tk.LEFT, padx=5)

    window.mainloop()

def create_tray():
    try:
        import pystray
        from PIL import Image, ImageDraw

        icon_image = Image.new('RGB', (64, 64), color='black')
        d = ImageDraw.Draw(icon_image)
        d.rectangle([16, 16, 48, 48], fill='cyan')

        def on_quit(icon, item):
            icon.stop()
            os._exit(0)

        menu = pystray.Menu(
            pystray.MenuItem(" CopyPasteBasedEmojiRemover", lambda: None, default=True),
            pystray.MenuItem("Quit", on_quit)
        )
        icon = pystray.Icon("pasre", icon_image, "CopyPasteBasedEmojiRemover", menu)
        icon.run()
    except ImportError:
        pass

if __name__ == "__main__":
    try:
        lock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lock_socket.bind(('127.0.0.1', 49152))
    except OSError:
        print("Another instance of CopyPasteBasedEmojiRemover is already running.")
        sys.exit(1)

    print("=" * 50)
    print(" CopyPasteBasedEmojiRemover Prototype")
    print(f"Config: {CONFIG_PATH}")
    print("\nHotkeys:")
    print("  Ctrl+V          → Remove emojis and paste, or flush & transform stack")
    print("  Ctrl+Alt+C      → Copy current selection to stack")
    print("  Ctrl+Alt+V      → Open last 5 copied items (click to paste)")
    print("\nRun as Admin for best results.\n")

    keyboard.add_hotkey('ctrl+v', on_paste, suppress=True)
    keyboard.add_hotkey('ctrl+alt+c', copy_to_stack)
    keyboard.add_hotkey('ctrl+alt+v', show_history)
    keyboard.add_hotkey('ctrl+c', on_copy)

    tray_thread = threading.Thread(target=create_tray, daemon=True)
    tray_thread.start()

    print(" Ready. Press Ctrl+C in terminal to stop.")
    keyboard.wait()
