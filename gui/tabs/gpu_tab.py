from tkinter import Frame, Label
from gui.scrolling_graph import ScrollingGraph

def create_gpu_tab(notebook, data_history, colors, labels):
    gpu_frame = Frame(notebook, bg=colors['bg'])
    notebook.add(gpu_frame, text="GPU")
    graph = ScrollingGraph(gpu_frame, data_history['gpu_usage'], colors['warning'], 0, 100, seconds=10, bg=colors['chart_bg'], grid=colors['chart_grid'], label='GPU Usage (%)', label_color=colors['fg'])
    graph.pack(fill='both', expand=True, padx=10, pady=10)
    graph.start()
    details_frame = Frame(gpu_frame, bg=colors['secondary'], relief='raised', bd=1)
    details_frame.pack(fill='x', padx=10, pady=(0, 10))
    fields = [
        ("Name", "gpu_name"),
        ("Usage", "gpu_usage"),
        ("Memory Used", "gpu_mem_used"),
        ("Memory Total", "gpu_mem_total"),
        ("Memory Usage", "gpu_mem_usage"),
        ("Temperature", "gpu_temp"),
        ("Frequency", "gpu_freq"),
        ("Memory Frequency", "gpu_mem_freq"),
        ("Voltage", "gpu_voltage"),
        ("Max TGP", "gpu_max_tgp"),
        ("Fan Speed", "gpu_fan")
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
    return gpu_frame 