from tkinter import Frame, Label
from gui.scrolling_graph import ScrollingGraph

def create_fan_tab(notebook, data_history, colors, labels):
    fan_frame = Frame(notebook, bg=colors['bg'])
    notebook.add(fan_frame, text="Fans")
    graph = ScrollingGraph(fan_frame, data_history['fan_speeds'], colors['info'], 0, 5000, seconds=10, bg=colors['chart_bg'], grid=colors['chart_grid'], label='Fan Speed (RPM)', label_color=colors['fg'])
    graph.pack(fill='both', expand=True, padx=10, pady=10)
    graph.start()
    details_frame = Frame(fan_frame, bg=colors['secondary'], relief='raised', bd=1)
    details_frame.pack(fill='x', padx=10, pady=(0, 10))
    fields = [
        ("CPU Fan", "cpu_fan"),
        ("GPU Fan", "gpu_fan_speed"),
        ("System Fans", "sys_fans")
    ]
    for i, (label_text, key) in enumerate(fields):
        row = i // 3
        col = i % 3
        field_frame = Frame(details_frame, bg=colors['secondary'])
        field_frame.grid(row=row, column=col, sticky="ew", padx=10, pady=5)
        label = Label(field_frame, text=f"{label_text}:", font=("Segoe UI", 10), bg=colors['secondary'], fg=colors['fg'])
        label.pack(anchor="w")
        value_label = Label(field_frame, text="Loading...", font=("Consolas", 10), bg=colors['secondary'], fg=colors['success'])
        value_label.pack(anchor="w")
        labels[key] = value_label
    for i in range(3):
        details_frame.grid_columnconfigure(i, weight=1)
    return fan_frame 