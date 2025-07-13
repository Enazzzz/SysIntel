from tkinter import Frame
from gui.scrolling_graph import ScrollingGraph

def create_cpu_tab(notebook, data_history, colors, labels):
    cpu_frame = Frame(notebook, bg=colors['bg'])
    notebook.add(cpu_frame, text="CPU")
    graph = ScrollingGraph(cpu_frame, data_history['cpu_usage'], colors['accent'], 0, 100, seconds=10, bg=colors['chart_bg'], grid=colors['chart_grid'], label='CPU Usage (%)', label_color=colors['fg'])
    graph.pack(fill='both', expand=True, padx=10, pady=10)
    graph.start()
    details_frame = Frame(cpu_frame, bg=colors['secondary'], relief='raised', bd=1)
    details_frame.pack(fill='x', padx=10, pady=(0, 10))
    # Details grid
    fields = [
        ("Name", "cpu_name"),
        ("Cores", "cpu_cores"),
        ("Current Usage", "cpu_usage"),
        ("Frequency", "cpu_freq"),
        ("Temperature", "cpu_temp"),
        ("Voltage", "cpu_voltage")
    ]
    for i, (label_text, key) in enumerate(fields):
        row = i // 3
        col = i % 3
        field_frame = Frame(details_frame, bg=colors['secondary'])
        field_frame.grid(row=row, column=col, sticky="ew", padx=10, pady=5)
        from tkinter import Label
        label = Label(field_frame, text=f"{label_text}:", font=("Segoe UI", 10), bg=colors['secondary'], fg=colors['fg'])
        label.pack(anchor="w")
        value_label = Label(field_frame, text="Loading...", font=("Consolas", 10), bg=colors['secondary'], fg=colors['success'])
        value_label.pack(anchor="w")
        labels[key] = value_label
    for i in range(3):
        details_frame.grid_columnconfigure(i, weight=1)
    return cpu_frame 