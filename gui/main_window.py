import tkinter as tk
from tkinter import ttk
from monitor import get_system_snapshot
from utils import format_bytes, format_frequency, format_temperature, format_voltage, format_power, format_speed
import platform
from collections import deque
import time
import math
from gui.scrolling_graph import ScrollingGraph
import os
import json
from gui.dual_line_graph import DualLineGraph
import sys
import csv
import base64

class SysIntelGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SysIntel - Advanced System Monitor")
        self.root.geometry("1400x900")
        self.root.resizable(True, True)
        
        # Dark theme colors
        self.colors = {
            'bg': '#1e1e1e',
            'fg': '#ffffff',
            'accent': '#007acc',
            'secondary': '#2d2d30',
            'success': '#4caf50',
            'warning': '#ff9800',
            'danger': '#f44336',
            'info': '#2196f3',
            'chart_bg': '#2d2d30',
            'chart_grid': '#404040'
        }
        
        self.root.configure(bg=self.colors['bg'])
        self.labels = {}
        self.graphs = {}
        self.history_seconds = 60  # Always show 60 seconds (Task Manager style)
        self.config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        self.smoothing_style = 'round'  # Default smoothing style
        self.update_interval = 500  # Default 0.5 seconds
        self.temp_unit = 'C'  # Default temperature unit
        self.update_stats_after_id = None
        self.load_config()
        self._set_data_history_length()
        self.build_ui()
        self.update_stats()

    def load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                if 'update_interval' in config:
                    self.update_interval = int(config['update_interval'])
                if 'smoothing_style' in config:
                    self.smoothing_style = config['smoothing_style']
                if 'temp_unit' in config:
                    self.temp_unit = config['temp_unit']
        except Exception as e:
            print(f"Error loading config: {e}")

    def save_config(self):
        try:
            config = {
                'update_interval': self.update_interval,
                'smoothing_style': self.smoothing_style,
                'temp_unit': self.temp_unit
            }
            with open(self.config_path, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Error saving config: {e}")

    def _set_data_history_length(self):
        points = max(2, int(math.ceil(self.history_seconds * 1000 / self.update_interval)))
        self.data_history = {
            'cpu_usage': deque(maxlen=points),
            'memory_usage': deque(maxlen=points),
            'gpu_usage': deque(maxlen=points),
            'gpu_temp': deque(maxlen=points),
            'cpu_temp': deque(maxlen=points),
            'fan_speeds': deque(maxlen=points)
        }

    def build_ui(self):
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_container, text="SysIntel - Advanced System Monitor", 
                              font=("Segoe UI", 20, "bold"), 
                              bg=self.colors['bg'], fg=self.colors['accent'])
        title_label.pack(pady=(0, 10))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Configure notebook style for dark theme
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background=self.colors['bg'])
        style.configure('TNotebook.Tab', background=self.colors['secondary'], foreground=self.colors['fg'])
        style.map('TNotebook.Tab', background=[('selected', self.colors['accent'])])
        
        # Create tabs
        self.create_cpu_tab()
        self.create_memory_tab()
        self.create_gpu_tab()
        self.create_fan_tab()
        self.create_network_tab()
        self.create_system_tab()
        self.create_temp_tab()  # Add temperature tab
        self.create_settings_tab()
        
        # Create bottom panel for non-graphable data
        self.create_bottom_panel(main_container)
        # Bind tab change to force redraw
        self.notebook.bind('<<NotebookTabChanged>>', lambda e: self.update_graphs())

    def create_cpu_tab(self):
        """Create CPU monitoring tab with graphs"""
        cpu_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(cpu_frame, text="CPU")
        # CPU Usage graph
        graph = ScrollingGraph(cpu_frame, self.data_history['cpu_usage'], self.colors['accent'], 0, 100, seconds=self.history_seconds, bg=self.colors['chart_bg'], grid=self.colors['chart_grid'], label='CPU Usage (%)', label_color=self.colors['fg'], smoothing=self.smoothing_style)
        graph.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 0))
        self.graphs['cpu'] = graph
        # CPU details panel
        details_frame = tk.Frame(cpu_frame, bg=self.colors['secondary'], relief=tk.RAISED, bd=1)
        details_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        # Create CPU details
        self.create_detail_grid(details_frame, [
            ("Name", "cpu_name"),
            ("Cores", "cpu_cores"),
            ("Current Usage", "cpu_usage"),
            ("Frequency", "cpu_freq"),
            ("Temperature", "cpu_temp"),
            ("Voltage", "cpu_voltage")
        ])

    def create_memory_tab(self):
        """Create Memory monitoring tab with graphs"""
        memory_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(memory_frame, text="Memory")
        
        # Create graph
        graph = ScrollingGraph(memory_frame, self.data_history['memory_usage'], self.colors['success'], 0, 100, seconds=self.history_seconds, bg=self.colors['chart_bg'], grid=self.colors['chart_grid'], label='Memory Usage (%)', label_color=self.colors['fg'], smoothing=self.smoothing_style)
        graph.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.graphs['memory'] = graph
        
        # Memory details panel
        details_frame = tk.Frame(memory_frame, bg=self.colors['secondary'], relief=tk.RAISED, bd=1)
        details_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Create memory details
        self.create_detail_grid(details_frame, [
            ("Total RAM", "mem_total"),
            ("Used RAM", "mem_used"),
            ("Available RAM", "mem_available"),
            ("Usage Percentage", "mem_usage"),
            ("Frequency", "mem_freq")
        ])

    def create_gpu_tab(self):
        """Create GPU monitoring tab with graphs"""
        gpu_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(gpu_frame, text="GPU")
        
        # Create graph
        graph = ScrollingGraph(gpu_frame, self.data_history['gpu_usage'], self.colors['warning'], 0, 100, seconds=self.history_seconds, bg=self.colors['chart_bg'], grid=self.colors['chart_grid'], label='GPU Usage (%)', label_color=self.colors['fg'], smoothing=self.smoothing_style)
        graph.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.graphs['gpu'] = graph
        
        # GPU details panel
        details_frame = tk.Frame(gpu_frame, bg=self.colors['secondary'], relief=tk.RAISED, bd=1)
        details_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Create GPU details
        self.create_detail_grid(details_frame, [
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
        ])

    def create_fan_tab(self):
        """Create Fan monitoring tab with graphs"""
        fan_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(fan_frame, text="Fans")
        
        # Create graph
        graph = ScrollingGraph(fan_frame, self.data_history['fan_speeds'], self.colors['info'], 0, 5000, seconds=self.history_seconds, bg=self.colors['chart_bg'], grid=self.colors['chart_grid'], label='Fan Speed (RPM)', label_color=self.colors['fg'], smoothing=self.smoothing_style)
        graph.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.graphs['fans'] = graph
        
        # Fan details panel
        details_frame = tk.Frame(fan_frame, bg=self.colors['secondary'], relief=tk.RAISED, bd=1)
        details_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Create fan details
        self.create_detail_grid(details_frame, [
            ("CPU Fan", "cpu_fan"),
            ("GPU Fan", "gpu_fan_speed"),
            ("System Fans", "sys_fans")
        ])

    def create_network_tab(self):
        """Create Network monitoring tab"""
        network_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(network_frame, text="Network")
        
        # Network details panel (no graph for network)
        details_frame = tk.Frame(network_frame, bg=self.colors['secondary'], relief=tk.RAISED, bd=1)
        details_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create network details
        self.create_detail_grid(details_frame, [
            ("Total Sent", "net_sent"),
            ("Total Received", "net_recv"),
            ("Ethernet Adapters", "eth_adapters"),
            ("Wi-Fi Adapters", "wifi_adapters")
        ])

    def create_system_tab(self):
        """Create System information tab"""
        system_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(system_frame, text="System")
        
        # System details panel (no graph for system info)
        details_frame = tk.Frame(system_frame, bg=self.colors['secondary'], relief=tk.RAISED, bd=1)
        details_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create system details
        self.create_detail_grid(details_frame, [
            ("Platform", "platform"),
            ("Hostname", "hostname"),
            ("Machine", "machine"),
            ("Partitions", "disk_partitions"),
            ("File Systems", "disk_types")
        ])

    def create_temp_tab(self):
        temp_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(temp_frame, text="Temperature")
        # Determine Y axis range and label
        if self.temp_unit == 'F':
            y_min, y_max = 32, 230
            label = 'Temperature (°F)'
        else:
            y_min, y_max = 0, 110
            label = 'Temperature (°C)'
        self.graphs['temp_tab'] = DualLineGraph(temp_frame,
            [self.data_history['cpu_temp'], self.data_history['gpu_temp']],
            [self.colors['danger'], self.colors['warning']],
            y_min=y_min, y_max=y_max, seconds=self.history_seconds,
            bg=self.colors['chart_bg'], grid=self.colors['chart_grid'],
            label=label, label_color=self.colors['fg'],
            smoothing=self.smoothing_style,
            legends=[('CPU Temp', self.colors['danger']), ('GPU Temp', self.colors['warning'])]
        )
        self.graphs['temp_tab'].pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def create_settings_tab(self):
        """Create Settings tab for configuration"""
        settings_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(settings_frame, text="Settings")
        
        # Settings container
        settings_container = tk.Frame(settings_frame, bg=self.colors['secondary'], relief=tk.RAISED, bd=1)
        settings_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(settings_container, text="System Monitor Settings", 
                              font=("Segoe UI", 16, "bold"), 
                              bg=self.colors['secondary'], fg=self.colors['accent'])
        title_label.pack(pady=(20, 30))
        
        # Update frequency setting
        update_frame = tk.Frame(settings_container, bg=self.colors['secondary'])
        update_frame.pack(fill=tk.X, padx=30, pady=20)
        
        # Update frequency label
        update_label = tk.Label(update_frame, text="Update Frequency:", 
                               font=("Segoe UI", 12, "bold"), 
                               bg=self.colors['secondary'], fg=self.colors['fg'])
        update_label.pack(anchor="w", pady=(0, 10))
        
        # Update frequency description
        update_desc = tk.Label(update_frame, 
                              text="How often the system monitor updates data and graphs.\nUltra Fast (0.1s) = Real-time gaming monitoring\nLower values = more frequent updates but higher CPU usage.", 
                              font=("Segoe UI", 10), 
                              bg=self.colors['secondary'], fg=self.colors['fg'],
                              justify=tk.LEFT)
        update_desc.pack(anchor="w", pady=(0, 15))
        
        # Update frequency slider frame
        slider_frame = tk.Frame(update_frame, bg=self.colors['secondary'])
        slider_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Update frequency slider
        self.update_slider = tk.Scale(slider_frame, 
                                     from_=100, to=10000, 
                                     orient=tk.HORIZONTAL,
                                     resolution=100,
                                     bg=self.colors['secondary'],
                                     fg=self.colors['fg'],
                                     highlightbackground=self.colors['secondary'],
                                     troughcolor=self.colors['chart_grid'],
                                     activebackground=self.colors['accent'])
        self.update_slider.set(self.update_interval)
        self.update_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Update frequency value label
        self.update_value_label = tk.Label(slider_frame, 
                                          text=f"{self.update_interval/1000:.1f}s", 
                                          font=("Consolas", 12), 
                                          bg=self.colors['secondary'], fg=self.colors['accent'])
        self.update_value_label.pack(side=tk.RIGHT)
        
        # Bind slider to update function
        self.update_slider.config(command=self.on_update_interval_change)
        
        # Preset buttons frame
        preset_frame = tk.Frame(update_frame, bg=self.colors['secondary'])
        preset_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Preset buttons
        presets = [
            ("Ultra Fast (0.1s)", 100),
            ("Lightning (0.2s)", 200),
            ("Fast (0.5s)", 500),
            ("Normal (2s)", 2000),
            ("Slow (5s)", 5000),
            ("Very Slow (10s)", 10000)
        ]
        
        for preset_name, preset_value in presets:
            preset_btn = tk.Button(preset_frame, 
                                  text=preset_name,
                                  command=lambda v=preset_value: self.set_update_interval(v),
                                  bg=self.colors['accent'],
                                  fg=self.colors['fg'],
                                  font=("Segoe UI", 10),
                                  relief=tk.FLAT,
                                  padx=15,
                                  pady=5)
            preset_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Apply button
        apply_frame = tk.Frame(settings_container, bg=self.colors['secondary'])
        apply_frame.pack(fill=tk.X, padx=30, pady=(30, 20))
        
        apply_btn = tk.Button(apply_frame, 
                             text="Apply Settings",
                             command=self.apply_settings,
                             bg=self.colors['success'],
                             fg=self.colors['fg'],
                             font=("Segoe UI", 12, "bold"),
                             relief=tk.FLAT,
                             padx=30,
                             pady=10)
        apply_btn.pack(side=tk.LEFT, padx=(0, 10))
        # Reset Log button
        reset_log_btn = tk.Button(apply_frame,
                                 text="Reset Log",
                                 command=self.reset_log,
                                 bg=self.colors['danger'],
                                 fg=self.colors['fg'],
                                 font=("Segoe UI", 12, "bold"),
                                 relief=tk.FLAT,
                                 padx=30,
                                 pady=10)
        reset_log_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Status label
        self.status_label = tk.Label(settings_container, 
                                    text="Settings saved! Monitor will update every 2.0 seconds.", 
                                    font=("Segoe UI", 10), 
                                    bg=self.colors['secondary'], fg=self.colors['success'])
        self.status_label.pack(pady=(10, 20))

        # Smoothing style option
        smoothing_label = tk.Label(settings_container, text="Graph Smoothing:", font=("Segoe UI", 12, "bold"), bg=self.colors['secondary'], fg=self.colors['fg'])
        smoothing_label.pack(anchor="w", padx=30, pady=(10, 0))
        smoothing_frame = tk.Frame(settings_container, bg=self.colors['secondary'])
        smoothing_frame.pack(anchor="w", padx=30, pady=(0, 10))
        self.smoothing_var = tk.StringVar(value=self.smoothing_style)
        for text, value in [("None (Sharp)", "none"), ("Average", "average"), ("Round Corners", "round")]:
            rb = tk.Radiobutton(smoothing_frame, text=text, variable=self.smoothing_var, value=value, bg=self.colors['secondary'], fg=self.colors['fg'], selectcolor=self.colors['accent'], command=self.on_smoothing_change)
            rb.pack(side=tk.LEFT, padx=(0, 15))

        # Temperature unit option
        temp_unit_label = tk.Label(settings_container, text="Temperature Unit:", font=("Segoe UI", 12, "bold"), bg=self.colors['secondary'], fg=self.colors['fg'])
        temp_unit_label.pack(anchor="w", padx=30, pady=(10, 0))
        temp_unit_frame = tk.Frame(settings_container, bg=self.colors['secondary'])
        temp_unit_frame.pack(anchor="w", padx=30, pady=(0, 10))
        self.temp_unit_var = tk.StringVar(value=self.temp_unit)
        for text, value in [("Celsius (°C)", "C"), ("Fahrenheit (°F)", "F")]:
            rb = tk.Radiobutton(temp_unit_frame, text=text, variable=self.temp_unit_var, value=value, bg=self.colors['secondary'], fg=self.colors['fg'], selectcolor=self.colors['accent'], command=self.on_temp_unit_change)
            rb.pack(side=tk.LEFT, padx=(0, 15))

    def create_bottom_panel(self, parent):
        """Create bottom panel for non-graphable data"""
        bottom_frame = tk.Frame(parent, bg=self.colors['secondary'], relief=tk.RAISED, bd=1)
        bottom_frame.pack(fill=tk.X, pady=(0, 4))  # Less vertical padding
        # Title for bottom panel
        title_label = tk.Label(bottom_frame, text="System Overview", 
                              font=("Segoe UI", 12, "bold"),  # Smaller font
                              bg=self.colors['secondary'], fg=self.colors['accent'])
        title_label.pack(pady=2)
        # Create overview grid (compact, single row)
        overview_frame = tk.Frame(bottom_frame, bg=self.colors['secondary'])
        overview_frame.pack(fill=tk.X, padx=6, pady=(0, 4))
        # Create overview details (single row, compact font)
        fields = [
            ("Platform", "platform"),
            ("CPU Usage", "cpu_usage"),
            ("Memory Usage", "mem_usage"),
            ("GPU Usage", "gpu_usage"),
            ("GPU Temp", "gpu_temp"),
            ("CPU Temp", "cpu_temp")
        ]
        for i, (label_text, key) in enumerate(fields):
            field_frame = tk.Frame(overview_frame, bg=self.colors['secondary'])
            field_frame.grid(row=0, column=i, sticky="ew", padx=6, pady=2)
            label = tk.Label(field_frame, text=f"{label_text}:", font=("Segoe UI", 9), bg=self.colors['secondary'], fg=self.colors['fg'])
            label.pack(anchor="w")
            value_label = tk.Label(field_frame, text="Loading...", font=("Consolas", 9), bg=self.colors['secondary'], fg=self.colors['success'])
            value_label.pack(anchor="w")
            self.labels[key] = value_label
        for i in range(len(fields)):
            overview_frame.grid_columnconfigure(i, weight=1)

    def create_detail_grid(self, parent, fields):
        """Create a grid of detail fields"""
        for i, (label_text, key) in enumerate(fields):
            row = i // 3  # 3 columns
            col = i % 3
            
            field_frame = tk.Frame(parent, bg=self.colors['secondary'])
            field_frame.grid(row=row, column=col, sticky="ew", padx=10, pady=5)
            
            label = tk.Label(field_frame, text=f"{label_text}:", 
                           font=("Segoe UI", 10), 
                           bg=self.colors['secondary'], fg=self.colors['fg'])
            label.pack(anchor="w")
            
            value_label = tk.Label(field_frame, text="Loading...", 
                                 font=("Consolas", 10), 
                                 bg=self.colors['secondary'], fg=self.colors['success'])
            value_label.pack(anchor="w")
            
            self.labels[key] = value_label
        
        # Configure grid weights
        for i in range(3):
            parent.grid_columnconfigure(i, weight=1)

    def update_stats(self):
        """Update all statistics and graphs"""
        try:
            stats = get_system_snapshot()
            # Efficiently log the new data point as compact CSV
            log_path = os.path.join(os.path.dirname(__file__), 'sysintel_log.csv')
            log_fields = ['ts', 'cpu', 'mem', 'gpu', 'ct', 'gt', 'fan']
            # Use base36 for timestamp for compactness
            ts = int(time.time())
            ts_b36 = base36encode(ts)
            row = {
                'ts': ts_b36,
                'cpu': int(round(stats['cpu']['usage'])),
                'mem': int(round(stats['memory']['percent'])),
                'gpu': int(round(stats['gpu']['usage'])),
                'ct': int(round(stats['cpu']['temperature'])),
                'gt': int(round(stats['gpu']['temperature'])),
                'fan': int(round(stats['fans']['cpu']))
            }
            write_header = not os.path.exists(log_path)
            with open(log_path, 'a', newline='', encoding='utf-8') as logf:
                writer = csv.DictWriter(logf, fieldnames=log_fields)
                if write_header:
                    writer.writeheader()
                writer.writerow(row)
            
            # Update data history
            self.data_history['cpu_usage'].append(stats['cpu']['usage'])
            self.data_history['memory_usage'].append(stats['memory']['percent'])
            self.data_history['gpu_usage'].append(stats['gpu']['usage'])
            
            # Convert temps if needed
            if self.temp_unit == 'F':
                cpu_temp = stats['cpu']['temperature'] * 9/5 + 32 if stats['cpu']['temperature'] else 0
                gpu_temp = stats['gpu']['temperature'] * 9/5 + 32 if stats['gpu']['temperature'] else 0
            else:
                cpu_temp = stats['cpu']['temperature']
                gpu_temp = stats['gpu']['temperature']
            self.data_history['cpu_temp'].append(cpu_temp)
            self.data_history['gpu_temp'].append(gpu_temp)
            
            # Update fan speeds (average of all fans)
            fan_speeds = [stats['fans']['cpu'], stats['fans']['gpu']] + stats['fans']['system']
            avg_fan_speed = sum(fan_speeds) / len(fan_speeds) if fan_speeds else 0
            self.data_history['fan_speeds'].append(avg_fan_speed)
            
            # Update graphs
            self.update_graphs()
            
            # Update labels
            self.update_all_labels(stats)
            
        except Exception as e:
            print(f"Error updating stats: {e}")
        # Schedule next update
        if self.update_stats_after_id:
            self.root.after_cancel(self.update_stats_after_id)
        self.update_stats_after_id = self.root.after(self.update_interval, self.update_stats)

    def on_update_interval_change(self, value):
        """Handle update interval slider change"""
        interval = int(value)
        self.update_value_label.config(text=f"{interval/1000:.1f}s")

    def set_update_interval(self, interval):
        """Set update interval from preset button"""
        self.update_slider.set(interval)
        self.update_value_label.config(text=f"{interval/1000:.1f}s")

    def apply_settings(self):
        """Apply the current settings"""
        new_interval = int(self.update_slider.get())
        new_smoothing = self.smoothing_var.get()
        new_temp_unit = self.temp_unit_var.get()
        changed = False
        if new_interval != self.update_interval:
            self.update_interval = new_interval
            self._set_data_history_length()  # Re-instantiate all deques with new maxlen
            changed = True
            # Immediately update stats to seed graphs and restart update loop
            if self.update_stats_after_id:
                self.root.after_cancel(self.update_stats_after_id)
                self.update_stats_after_id = None
            self.update_stats()
            # Schedule a second update to ensure 2 data points for graphs
            self.root.after(10, self.update_stats)
            # Force all graphs to redraw immediately
            for g in self.graphs.values():
                g.redraw()
        if new_smoothing != self.smoothing_style:
            self.smoothing_style = new_smoothing
            for g in self.graphs.values():
                g.smoothing = self.smoothing_style
                g.redraw()
            changed = True
        if new_temp_unit != self.temp_unit:
            self.temp_unit = new_temp_unit
            self.update_temp_tab_graph()
            changed = True
        # Save config
        self.save_config()
        # Restart the app immediately (no confirmation)
        python = sys.executable
        os.execl(python, python, *sys.argv)
        # Optimize performance based on update speed
        self.optimize_for_speed(self.update_interval)
        # Update status message
        self.status_label.config(text=f"Settings saved! Monitor will update every {self.update_interval/1000:.1f} seconds.")
        # Show success message briefly
        self.status_label.config(fg=self.colors['success'])
        self.root.after(3000, lambda: self.status_label.config(fg=self.colors['fg']))

    def optimize_for_speed(self, interval):
        # No longer needed for history length, but keep for future optimizations
        pass

    def update_graphs(self):
        """Update all graphs with new data - Task Manager style scrolling"""
        if 'cpu' in self.graphs:
            self.graphs['cpu'].redraw()
        if 'memory' in self.graphs:
            self.graphs['memory'].redraw()
        if 'gpu' in self.graphs:
            self.graphs['gpu'].redraw()
        if 'fans' in self.graphs:
            self.graphs['fans'].redraw()
        if 'temp' in self.graphs:
            self.graphs['temp'].redraw()
        if 'temp_tab' in self.graphs:
            self.graphs['temp_tab'].redraw()

    def update_all_labels(self, stats):
        """Update all labels with current statistics"""
        # System Info
        self.update_label("platform", f"{stats['system']['platform']} {stats['system']['release']}")
        self.update_label("hostname", stats['system']['hostname'])
        self.update_label("machine", stats['system']['machine'])
        # CPU Info
        self.update_label("cpu_name", stats['cpu']['name'])
        self.update_label("cpu_usage", f"{stats['cpu']['usage']:.1f}%")
        self.update_label("cpu_cores", str(stats['cpu']['cores']))
        self.update_label("cpu_freq", f"{stats['cpu']['frequency']/1000:.1f} GHz" if stats['cpu']['frequency'] > 0 else "N/A")
        self.update_label("cpu_temp", f"{stats['cpu']['temperature']:.1f}°C" if stats['cpu']['temperature'] > 0 else "N/A")
        self.update_label("cpu_voltage", f"{stats['cpu']['voltage']:.3f}V" if stats['cpu']['voltage'] > 0 else "N/A")
        # Memory Info
        self.update_label("mem_total", format_bytes(stats['memory']['total']))
        self.update_label("mem_used", format_bytes(stats['memory']['used']))
        self.update_label("mem_available", format_bytes(stats['memory']['available']))
        self.update_label("mem_usage", f"{stats['memory']['percent']:.1f}%")
        self.update_label("mem_freq", f"{stats['memory']['frequency']} MHz" if stats['memory']['frequency'] > 0 else "N/A")
        # GPU Info
        self.update_label("gpu_name", stats['gpu']['name'])
        self.update_label("gpu_usage", f"{stats['gpu']['usage']:.1f}%" if stats['gpu']['usage'] > 0 else "N/A")
        self.update_label("gpu_mem_used", format_bytes(stats['gpu']['memory_used']) if stats['gpu']['memory_used'] > 0 else "N/A")
        self.update_label("gpu_mem_total", format_bytes(stats['gpu']['memory_total']) if stats['gpu']['memory_total'] > 0 else "N/A")
        self.update_label("gpu_mem_usage", f"{stats['gpu']['memory_percent']:.1f}%" if stats['gpu']['memory_percent'] > 0 else "N/A")
        self.update_label("gpu_temp", f"{stats['gpu']['temperature']:.1f}°C" if stats['gpu']['temperature'] > 0 else "N/A")
        self.update_label("gpu_freq", f"{stats['gpu']['frequency']} MHz" if stats['gpu']['frequency'] > 0 else "N/A")
        self.update_label("gpu_mem_freq", f"{stats['gpu']['memory_frequency']} MHz" if stats['gpu']['memory_frequency'] > 0 else "N/A")
        self.update_label("gpu_voltage", f"{stats['gpu']['voltage']:.3f}V" if stats['gpu']['voltage'] > 0 else "N/A")
        self.update_label("gpu_max_tgp", f"{stats['gpu']['max_tgp']}W" if stats['gpu']['max_tgp'] > 0 else "N/A")
        self.update_label("gpu_fan", f"{stats['gpu']['fan_speed']:.0f} RPM" if stats['gpu']['fan_speed'] > 0 else "N/A")
        # Fan Info
        self.update_label("cpu_fan", f"{stats['fans']['cpu']:.0f} RPM" if stats['fans']['cpu'] > 0 else "N/A")
        self.update_label("gpu_fan_speed", f"{stats['fans']['gpu']:.0f} RPM" if stats['fans']['gpu'] > 0 else "N/A")
        sys_fans_text = ", ".join([f"{fan:.0f}" for fan in stats['fans']['system']]) if stats['fans']['system'] else "N/A"
        self.update_label("sys_fans", sys_fans_text)
        # Network Info
        self.update_label("net_sent", format_bytes(stats['network']['total_sent']))
        self.update_label("net_recv", format_bytes(stats['network']['total_recv']))
        eth_adapters = [adapter['name'] for adapter in stats['network']['adapters'] if adapter['type'] == 'Ethernet']
        self.update_label("eth_adapters", ", ".join(eth_adapters) if eth_adapters else "None")
        wifi_adapters = [adapter['name'] for adapter in stats['network']['adapters'] if adapter['type'] == 'Wi-Fi']
        self.update_label("wifi_adapters", ", ".join(wifi_adapters) if wifi_adapters else "None")
        # Disk Info
        partitions_text = f"{len(stats['disk']['partitions'])} partitions"
        self.update_label("disk_partitions", partitions_text)
        types_text = ", ".join(set(stats['disk']['types'])) if stats['disk']['types'] else "None"
        self.update_label("disk_types", types_text)

    def update_label(self, key, value):
        """Update a specific label with color coding"""
        if key in self.labels:
            label = self.labels[key]
            label.config(text=value)
            
            # Color coding based on values
            if "usage" in key or "percent" in key:
                try:
                    val = float(value.replace('%', ''))
                    if val > 80:
                        label.config(fg=self.colors['danger'])
                    elif val > 60:
                        label.config(fg=self.colors['warning'])
                    else:
                        label.config(fg=self.colors['success'])
                except:
                    label.config(fg=self.colors['fg'])
            elif "temp" in key:
                try:
                    val = float(value.replace('°C', ''))
                    if val > 80:
                        label.config(fg=self.colors['danger'])
                    elif val > 60:
                        label.config(fg=self.colors['warning'])
                    else:
                        label.config(fg=self.colors['success'])
                except:
                    label.config(fg=self.colors['fg'])
            else:
                label.config(fg=self.colors['fg'])

    def on_smoothing_change(self):
        self.smoothing_style = self.smoothing_var.get()
        for g in self.graphs.values():
            g.smoothing = self.smoothing_style
            g.redraw()

    def on_temp_unit_change(self):
        self.temp_unit = self.temp_unit_var.get()
        self.update_temp_tab_graph()

    def update_temp_tab_graph(self):
        # Recreate the temp graph with the new unit
        temp_frame = self.graphs['temp_tab'].master
        self.graphs['temp_tab'].destroy()
        if self.temp_unit == 'F':
            y_min, y_max = 32, 230
            label = 'Temperature (°F)'
        else:
            y_min, y_max = 0, 110
            label = 'Temperature (°C)'
        self.graphs['temp_tab'] = DualLineGraph(temp_frame,
            [self.data_history['cpu_temp'], self.data_history['gpu_temp']],
            [self.colors['danger'], self.colors['warning']],
            y_min=y_min, y_max=y_max, seconds=self.history_seconds,
            bg=self.colors['chart_bg'], grid=self.colors['chart_grid'],
            label=label, label_color=self.colors['fg'],
            smoothing=self.smoothing_style,
            legends=[('CPU Temp', self.colors['danger']), ('GPU Temp', self.colors['warning'])]
        )
        self.graphs['temp_tab'].pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def reset_log(self):
        log_path = os.path.join(os.path.dirname(__file__), 'sysintel_log.csv')
        try:
            if os.path.exists(log_path):
                with open(log_path, 'w', encoding='utf-8') as f:
                    f.write('ts,cpu,mem,gpu,ct,gt,fan\n')
            self.status_label.config(text="Log reset!", fg=self.colors['success'])
        except Exception as e:
            self.status_label.config(text=f"Error resetting log: {e}", fg=self.colors['danger'])

def base36encode(number):
    """Convert an integer to a base36 string."""
    if not isinstance(number, int):
        raise TypeError('number must be an integer')
    if number < 0:
        raise ValueError('number must be positive')
    alphabet = '0123456789abcdefghijklmnopqrstuvwxyz'
    if number == 0:
        return '0'
    base36 = ''
    while number:
        number, i = divmod(number, 36)
        base36 = alphabet[i] + base36
    return base36

def run_gui():
    root = tk.Tk()
    app = SysIntelGUI(root)
    root.mainloop()
