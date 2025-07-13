import psutil
import platform
import subprocess
import re
import os

def get_cpu_detailed_info():
    """Get detailed CPU information including frequency, temp, voltage"""
    cpu_info = {
        "name": platform.processor(),
        "cores": psutil.cpu_count(),
        "usage": psutil.cpu_percent(),
        "frequency": 0,
        "temperature": 0,
        "voltage": 0
    }
    
    # Get CPU frequency
    try:
        cpu_freq = psutil.cpu_freq()
        if cpu_freq:
            cpu_info["frequency"] = cpu_freq.current
    except:
        pass
    
    # Get CPU temperature (Windows)
    if platform.system() == "Windows":
        try:
            import wmi
            c = wmi.WMI(namespace="root\\OpenHardwareMonitor")
            cpu_temp = c.Sensor()
            for sensor in cpu_temp:
                if sensor.SensorType == 'Temperature' and 'CPU' in sensor.Name:
                    cpu_info["temperature"] = sensor.Value
                    break
        except:
            pass
    
    return cpu_info

def get_memory_detailed_info():
    """Get detailed memory information"""
    mem = psutil.virtual_memory()
    return {
        "total": mem.total,
        "used": mem.used,
        "available": mem.available,
        "percent": mem.percent,
        "frequency": 0  # Will be filled by hardware-specific methods
    }

def get_gpu_detailed_info():
    """Get comprehensive GPU information"""
    gpu_info = {
        "name": "Unknown",
        "usage": 0,
        "memory_used": 0,
        "memory_total": 0,
        "memory_percent": 0,
        "temperature": 0,
        "frequency": 0,
        "memory_frequency": 0,
        "voltage": 0,
        "max_tgp": 0,
        "fan_speed": 0
    }
    # Try NVIDIA/AMD GPUs first
    try:
        import GPUtil
        gpus = GPUtil.getGPUs()
        if gpus:
            # Prefer dedicated GPU: highest memory and name contains NVIDIA/RTX/AMD/GPU
            def is_dedicated(gpu):
                name = gpu.name.upper()
                return any(x in name for x in ["NVIDIA", "RTX", "AMD", "GPU"])
            # Filter for dedicated
            dedicated_gpus = [gpu for gpu in gpus if is_dedicated(gpu)]
            if dedicated_gpus:
                gpu = max(dedicated_gpus, key=lambda g: g.memoryTotal)
            else:
                gpu = max(gpus, key=lambda g: g.memoryTotal)
            gpu_info.update({
                "name": gpu.name,
                "usage": gpu.load * 100,
                "memory_used": gpu.memoryUsed,
                "memory_total": gpu.memoryTotal,
                "memory_percent": (gpu.memoryUsed / gpu.memoryTotal) * 100 if gpu.memoryTotal else 0,
                "temperature": gpu.temperature
            })
    except ImportError:
        pass
    # Try AMD GPUs (Windows)
    if platform.system() == "Windows":
        try:
            import wmi
            c = wmi.WMI()
            gpu_controllers = c.Win32_VideoController()
            if gpu_controllers:
                # Prefer dedicated GPU by name
                def is_dedicated_wmi(name):
                    name = name.upper()
                    return any(x in name for x in ["NVIDIA", "RTX", "AMD", "GPU"])
                dedicated = [g for g in gpu_controllers if is_dedicated_wmi(g.Name)]
                if dedicated:
                    gpu_info["name"] = dedicated[0].Name
                else:
                    gpu_info["name"] = gpu_controllers[0].Name
        except:
            pass
    return gpu_info

def get_fan_speeds():
    """Get fan speeds for CPU, GPU, and system fans"""
    fans = {
        "cpu": 0,
        "gpu": 0,
        "system": []
    }
    
    if platform.system() == "Windows":
        try:
            import wmi
            c = wmi.WMI(namespace="root\\OpenHardwareMonitor")
            sensors = c.Sensor()
            for sensor in sensors:
                if sensor.SensorType == 'Fan':
                    if 'CPU' in sensor.Name:
                        fans["cpu"] = sensor.Value
                    elif 'GPU' in sensor.Name:
                        fans["gpu"] = sensor.Value
                    else:
                        fans["system"].append(sensor.Value)
        except:
            pass
    
    return fans

def get_network_detailed_info():
    """Get detailed network information"""
    net_info = {
        "adapters": [],
        "ethernet": {},
        "wifi": {},
        "total_sent": 0,
        "total_recv": 0
    }
    
    # Get network interfaces
    net_if_addrs = psutil.net_if_addrs()
    net_if_stats = psutil.net_if_stats()
    
    for interface, addrs in net_if_addrs.items():
        adapter_info = {
            "name": interface,
            "type": "Unknown",
            "speed": 0,
            "status": "Unknown"
        }
        
        # Determine adapter type
        if interface.startswith('Ethernet') or interface.startswith('eth'):
            adapter_info["type"] = "Ethernet"
        elif interface.startswith('Wi-Fi') or interface.startswith('wlan'):
            adapter_info["type"] = "Wi-Fi"
        
        # Get adapter status and speed
        if interface in net_if_stats:
            stats = net_if_stats[interface]
            adapter_info["status"] = "Up" if stats.isup else "Down"
            adapter_info["speed"] = stats.speed
        
        net_info["adapters"].append(adapter_info)
    
    # Get network usage
    net_io = psutil.net_io_counters()
    net_info["total_sent"] = net_io.bytes_sent
    net_info["total_recv"] = net_io.bytes_recv
    
    return net_info

def get_disk_detailed_info():
    """Get detailed disk information"""
    disk_info = {
        "partitions": [],
        "types": []
    }
    
    partitions = psutil.disk_partitions()
    for partition in partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            partition_info = {
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "filesystem": partition.fstype,
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
                "percent": usage.percent
            }
            disk_info["partitions"].append(partition_info)
            disk_info["types"].append(partition.fstype)
        except:
            pass
    
    return disk_info

def get_system_detailed_info():
    """Get comprehensive system information"""
    return {
        "platform": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "hostname": platform.node()
    }

def get_system_snapshot():
    """Get a comprehensive system snapshot"""
    return {
        "cpu": get_cpu_detailed_info(),
        "memory": get_memory_detailed_info(),
        "gpu": get_gpu_detailed_info(),
        "fans": get_fan_speeds(),
        "network": get_network_detailed_info(),
        "disk": get_disk_detailed_info(),
        "system": get_system_detailed_info()
    }
