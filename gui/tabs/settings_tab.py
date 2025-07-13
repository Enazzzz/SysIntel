from tkinter import Frame, Label, Scale, Button

def create_settings_tab(notebook, update_interval, set_update_interval_callback, colors):
    settings_frame = Frame(notebook, bg=colors['bg'])
    notebook.add(settings_frame, text="Settings")
    settings_container = Frame(settings_frame, bg=colors['secondary'], relief='raised', bd=1)
    settings_container.pack(fill='both', expand=True, padx=20, pady=20)
    title_label = Label(settings_container, text="System Monitor Settings", font=("Segoe UI", 16, "bold"), bg=colors['secondary'], fg=colors['accent'])
    title_label.pack(pady=(20, 30))
    update_frame = Frame(settings_container, bg=colors['secondary'])
    update_frame.pack(fill='x', padx=30, pady=20)
    update_label = Label(update_frame, text="Update Frequency:", font=("Segoe UI", 12, "bold"), bg=colors['secondary'], fg=colors['fg'])
    update_label.pack(anchor="w", pady=(0, 10))
    update_desc = Label(update_frame, text="How often the system monitor updates data and graphs.\nUltra Fast (0.1s) = Real-time gaming monitoring\nLower values = more frequent updates but higher CPU usage.", font=("Segoe UI", 10), bg=colors['secondary'], fg=colors['fg'], justify='left')
    update_desc.pack(anchor="w", pady=(0, 15))
    slider_frame = Frame(update_frame, bg=colors['secondary'])
    slider_frame.pack(fill='x', pady=(0, 10))
    update_slider = Scale(slider_frame, from_=100, to=10000, orient='horizontal', resolution=100, bg=colors['secondary'], fg=colors['fg'], highlightbackground=colors['secondary'], troughcolor=colors['chart_grid'], activebackground=colors['accent'])
    update_slider.set(update_interval)
    update_slider.pack(side='left', fill='x', expand=True, padx=(0, 10))
    update_value_label = Label(slider_frame, text=f"{update_interval/1000:.1f}s", font=("Consolas", 12), bg=colors['secondary'], fg=colors['accent'])
    update_value_label.pack(side='right')
    def on_slider(val):
        update_value_label.config(text=f"{int(val)/1000:.1f}s")
    update_slider.config(command=on_slider)
    preset_frame = Frame(update_frame, bg=colors['secondary'])
    preset_frame.pack(fill='x', pady=(10, 0))
    presets = [
        ("Ultra Fast (0.1s)", 100),
        ("Lightning (0.2s)", 200),
        ("Fast (0.5s)", 500),
        ("Normal (2s)", 2000),
        ("Slow (5s)", 5000),
        ("Very Slow (10s)", 10000)
    ]
    for preset_name, preset_value in presets:
        preset_btn = Button(preset_frame, text=preset_name, command=lambda v=preset_value: update_slider.set(v), bg=colors['accent'], fg=colors['fg'], font=("Segoe UI", 10), relief='flat', padx=15, pady=5)
        preset_btn.pack(side='left', padx=(0, 10))
    apply_frame = Frame(settings_container, bg=colors['secondary'])
    apply_frame.pack(fill='x', padx=30, pady=(30, 20))
    def apply():
        set_update_interval_callback(int(update_slider.get()))
    apply_btn = Button(apply_frame, text="Apply Settings", command=apply, bg=colors['success'], fg=colors['fg'], font=("Segoe UI", 12, "bold"), relief='flat', padx=30, pady=10)
    apply_btn.pack()
    return settings_frame 