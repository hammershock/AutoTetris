import os
import json
import tkinter as tk
from tkinter import ttk

config_file_path = 'settings.json'


def load_config():
    """加载配置文件，如果文件不存在则返回None。"""
    if os.path.exists(config_file_path):
        with open(config_file_path, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                pass
    return None


def save_config(settings):
    """将当前设置保存到配置文件。"""
    with open(config_file_path, 'w') as f:
        json.dump(settings, f, indent=4)


def launch_settings_window():
    # 尝试加载现有配置
    existing_settings = load_config()
    settings = {
        'width': 10,
        'height': 20,
        'autoplay': True,
        'turbo': True,
        'mode': 'easy',
        'drop_interval': 1.0,
        'fps': 60,
        'headless': False,
        'bag7': True,
        'instant_drop': True,
        'disable_auto_drop': False
    }

    # 如果存在配置文件，则更新默认设置
    if existing_settings:
        settings.update(existing_settings)

    success = False
    
    def on_start():
        settings['width'] = int(width_var.get())
        settings['height'] = int(height_var.get())
        settings['autoplay'] = autoplay_var.get()
        settings['turbo'] = turbo_var.get()
        settings['mode'] = mode_var.get()
        settings['drop_interval'] = float(drop_interval_var.get())
        settings['fps'] = int(fps_var.get())
        settings['headless'] = headless_var.get()
        settings['bag7'] = bag7_var.get()
        settings['instant_drop'] = instant_drop_var.get()
        settings['disable_auto_drop'] = disable_auto_drop_var.get()
        nonlocal success
        success = True
        save_config(settings)  # 保存设置
        root.destroy()
    
    root = tk.Tk()
    root.title("PyTris Settings")
    
    # Width and Height
    tk.Label(root, text="Width:").grid(row=0, column=0)
    width_var = tk.StringVar(value=str(settings['width']))
    tk.Entry(root, textvariable=width_var).grid(row=0, column=1)
    
    tk.Label(root, text="Height:").grid(row=1, column=0)
    height_var = tk.StringVar(value=str(settings['height']))
    tk.Entry(root, textvariable=height_var).grid(row=1, column=1)
    
    # Mode
    tk.Label(root, text="Mode:").grid(row=2, column=0)
    mode_var = tk.StringVar(value=settings['mode'])
    ttk.Combobox(root, textvariable=mode_var, values=['very-easy', 'easy', 'medium', 'hard', 'extreme']).grid(row=2,
                                                                                                              column=1)
    
    # Drop Interval
    tk.Label(root, text="Drop Interval:").grid(row=3, column=0)
    drop_interval_var = tk.StringVar(value=str(settings['drop_interval']))
    tk.Entry(root, textvariable=drop_interval_var).grid(row=3, column=1)
    
    # FPS
    tk.Label(root, text="FPS:").grid(row=4, column=0)
    fps_var = tk.StringVar(value=str(settings['fps']))
    tk.Entry(root, textvariable=fps_var).grid(row=4, column=1)
    
    # Checkboxes
    autoplay_var = tk.BooleanVar(value=settings['autoplay'])
    tk.Checkbutton(root, text="Autoplay", variable=autoplay_var).grid(row=5, column=0, columnspan=2)
    turbo_var = tk.BooleanVar(value=settings['turbo'])
    tk.Checkbutton(root, text="Turbo", variable=turbo_var).grid(row=6, column=0, columnspan=2)
    headless_var = tk.BooleanVar(value=settings['headless'])
    tk.Checkbutton(root, text="Headless", variable=headless_var).grid(row=7, column=0, columnspan=2)
    bag7_var = tk.BooleanVar(value=settings['bag7'])
    tk.Checkbutton(root, text="Enable Bag7", variable=bag7_var).grid(row=8, column=0, columnspan=2)
    instant_drop_var = tk.BooleanVar(value=settings['instant_drop'])
    tk.Checkbutton(root, text="Instant Drop", variable=instant_drop_var).grid(row=9, column=0, columnspan=2)
    disable_auto_drop_var = tk.BooleanVar(value=settings['disable_auto_drop'])
    tk.Checkbutton(root, text="Disable Auto Drop", variable=disable_auto_drop_var).grid(row=10, column=0, columnspan=2)
    
    # Start Button
    tk.Button(root, text="Start Game", command=on_start).grid(row=11, column=0, columnspan=2)
    
    root.mainloop()
    return settings, success
