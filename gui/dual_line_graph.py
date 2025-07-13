import tkinter as tk
import math

class DualLineGraph(tk.Canvas):
    def __init__(self, parent, data_sources, colors, y_min, y_max, seconds=10, bg='#222', grid='#444', label='', label_color='#fff', smoothing='average', legends=None, **kwargs):
        super().__init__(parent, bg=bg, highlightthickness=0, **kwargs)
        self.data_sources = data_sources  # List of deques
        self.colors = colors  # List of colors
        self.y_min = y_min
        self.y_max = y_max
        self.seconds = seconds
        self.bg = bg
        self.grid = grid
        self.label = label
        self.label_color = label_color
        self.smoothing = smoothing
        self.legends = legends or []
        self.bind('<Configure>', lambda e: self.redraw())

    def redraw(self):
        self.delete('all')
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 10 or h < 10:
            return
        # Draw grid
        max_points = max([ds.maxlen if hasattr(ds, 'maxlen') and ds.maxlen else len(ds) for ds in self.data_sources])
        time_per_point = self.seconds / (max_points - 1) if max_points > 1 else self.seconds
        n = max([len(ds) for ds in self.data_sources])
        filled_seconds = time_per_point * (n - 1)
        filled_width = w * (filled_seconds / self.seconds) if self.seconds > 0 else w
        left_edge = w - filled_width
        grid_spacing = self.seconds / 10
        for i in range(11):
            t = i * grid_spacing
            x = w - (t / self.seconds) * w
            if x < left_edge:
                continue
            self.create_line(x, 0, x, h, fill=self.grid, width=1, stipple='gray25')
        for i in range(5):
            y = h * i // 4
            self.create_line(left_edge, y, w, y, fill=self.grid, width=1, stipple='gray25')
        # Draw label
        if self.label:
            self.create_text(10, 10, anchor='nw', text=self.label, fill=self.label_color, font=('Segoe UI', 12, 'bold'))
        # Draw both lines
        for idx, ds in enumerate(self.data_sources):
            data = list(ds)
            color = self.colors[idx]
            n = len(data)
            valid_data = [v for v in data if v is not None and v != 0]
            if n < 2 or not valid_data:
                if n == 1 and valid_data:
                    # Draw a single point as a vertical line or dot at the right edge
                    v = data[-1]
                    x = w - 1
                    y = h - ((v - self.y_min) / (self.y_max - self.y_min)) * h
                    self.create_line(x, y-5, x, y+5, fill=color, width=2)
                continue
            if self.smoothing == 'average':
                smooth_data = self._moving_average(data, window=3)
            elif self.smoothing == 'round':
                smooth_data = self._round_corners(data, window=3)
            else:
                smooth_data = data
            interp_points = []
            if w > 2:
                for px in range(int(left_edge), w):
                    t = self.seconds * (w - px) / w
                    idx_float = (filled_seconds - t) / time_per_point if time_per_point > 0 else 0
                    idx0 = int(math.floor(idx_float))
                    idx1 = min(idx0 + 1, n - 1)
                    if idx0 < 0:
                        v = smooth_data[0]
                    elif idx1 >= n:
                        v = smooth_data[-1]
                    else:
                        v0, v1 = smooth_data[idx0], smooth_data[idx1]
                        frac = idx_float - idx0
                        v = v0 + (v1 - v0) * frac
                    y = h - ((v - self.y_min) / (self.y_max - self.y_min)) * h
                    interp_points.append((px, y))
            # Draw filled area under the line (optional, only for first line)
            if interp_points and idx == 0:
                area = [(interp_points[0][0], h)] + interp_points + [(interp_points[-1][0], h)]
                self.create_polygon(area, fill=color, outline='', stipple='gray50')
            # Draw the line on top
            if interp_points:
                for i in range(1, len(interp_points)):
                    self.create_line(interp_points[i-1][0], interp_points[i-1][1], interp_points[i][0], interp_points[i][1], fill=color, width=2)
        # Draw y-axis labels
        for i in range(5):
            y_val = self.y_max - (self.y_max - self.y_min) * i / 4
            y = h * i // 4
            self.create_text(left_edge + 5, y, anchor='nw', text=f'{y_val:.0f}', fill=self.label_color, font=('Consolas', 9))
        # Draw x-axis labels
        for i in range(6):
            t = self.seconds * i // 5
            x = w - (t / self.seconds) * w
            if x < left_edge:
                continue
            label = f'{self.seconds-t:.0f}s' if t > 0 else 'now'
            self.create_text(x, h-2, anchor='sw', text=label, fill=self.label_color, font=('Consolas', 9))
        # Draw legend
        if self.legends:
            legend_x = w - 120
            legend_y = 10
            for i, (text, color) in enumerate(self.legends):
                self.create_rectangle(legend_x, legend_y + i*22, legend_x+18, legend_y+16 + i*22, fill=color, outline='')
                self.create_text(legend_x+25, legend_y+8 + i*22, anchor='w', text=text, fill=self.label_color, font=('Segoe UI', 10, 'bold'))

    def _moving_average(self, data, window=3):
        n = len(data)
        if n < 2:
            return data
        result = []
        for i in range(n):
            vals = [data[j] for j in range(max(0, i-window//2), min(n, i+window//2+1)) if data[j] is not None]
            if vals:
                result.append(sum(vals)/len(vals))
            else:
                result.append(0)
        return result

    def _round_corners(self, data, window=3):
        n = len(data)
        if n < 3:
            return data
        result = list(data)
        for i in range(1, n-1):
            prev, curr, next_ = data[i-1], data[i], data[i+1]
            if prev is not None and curr is not None and next_ is not None:
                if abs(curr - prev) > abs(prev - next_) * 1.5 and abs(curr - next_) > abs(prev - next_) * 1.5:
                    result[i] = (prev + next_) / 2
        return result 