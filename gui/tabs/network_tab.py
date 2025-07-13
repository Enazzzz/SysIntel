from tkinter import Frame, Label

def create_network_tab(notebook, data_history, colors, labels):
    network_frame = Frame(notebook, bg=colors['bg'])
    notebook.add(network_frame, text="Network")
    details_frame = Frame(network_frame, bg=colors['secondary'], relief='raised', bd=1)
    details_frame.pack(fill='both', expand=True, padx=10, pady=10)
    fields = [
        ("Total Sent", "net_sent"),
        ("Total Received", "net_recv"),
        ("Ethernet Adapters", "eth_adapters"),
        ("Wi-Fi Adapters", "wifi_adapters")
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
    return network_frame 