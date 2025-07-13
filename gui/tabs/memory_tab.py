from tkinter import Frame, Label
from gui.scrolling_graph import ScrollingGraph

def create_memory_tab(notebook, data_history, colors, labels):
    memory_frame = Frame(notebook, bg=colors['bg'])
    notebook.add(memory_frame, text="Memory")
    graph = ScrollingGraph(memory_frame, data_history['memory_usage'], colors['success'], 0, 100, seconds=10, bg=colors['chart_bg'], grid=colors['chart_grid'], label='Memory Usage (%)', label_color=colors['fg'])
    graph.pack(fill='both', expand=True, padx=10, pady=10)
    graph.start()
    details_frame = Frame(memory_frame, bg=colors['secondary'], relief='raised', bd=1)
    details_frame.pack(fill='x', padx=10, pady=(0, 10))
    fields = [
        ("Total RAM", "mem_total"),
        ("Used RAM", "mem_used"),
        ("Available RAM", "mem_available"),
        ("Usage Percentage", "mem_usage"),
        ("Frequency", "mem_freq")
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
    return memory_frame 