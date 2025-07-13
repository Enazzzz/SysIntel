def format_bytes(bytes_):
    """Format bytes into human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_ < 1024:
            return f"{bytes_:.1f}{unit}"
        bytes_ /= 1024
    return f"{bytes_:.1f}PB"

def format_frequency(freq_hz):
    """Format frequency in Hz to appropriate unit"""
    if freq_hz >= 1e9:
        return f"{freq_hz/1e9:.1f} GHz"
    elif freq_hz >= 1e6:
        return f"{freq_hz/1e6:.1f} MHz"
    elif freq_hz >= 1e3:
        return f"{freq_hz/1e3:.1f} kHz"
    else:
        return f"{freq_hz:.0f} Hz"

def format_temperature(temp_celsius):
    """Format temperature with appropriate unit"""
    return f"{temp_celsius:.1f}°C"

def format_voltage(voltage_v):
    """Format voltage with appropriate unit"""
    return f"{voltage_v:.3f}V"

def format_power(power_w):
    """Format power with appropriate unit"""
    return f"{power_w:.1f}W"

def format_speed(speed_rpm):
    """Format fan speed"""
    return f"{speed_rpm:.0f} RPM"
