import psutil
import platform

def get_system_specs():
    specs = {}

    # Basic System Information
    specs['System'] = platform.system()
    specs['Node Name'] = platform.node()
    specs['Release'] = platform.release()
    specs['Version'] = platform.version()
    specs['Machine'] = platform.machine()
    specs['Processor'] = platform.processor()
    
    # CPU Info
    specs['CPU Cores'] = psutil.cpu_count(logical=False)
    specs['Logical CPUs'] = psutil.cpu_count(logical=True)
    specs['CPU Frequency'] = psutil.cpu_freq().current

    # Memory Info
    memory = psutil.virtual_memory()
    specs['Total RAM'] = f"{memory.total / (1024 ** 3):.2f} GB"
    specs['Available RAM'] = f"{memory.available / (1024 ** 3):.2f} GB"

    # Disk Info
    disk = psutil.disk_usage('/')
    specs['Total Disk Space'] = f"{disk.total / (1024 ** 3):.2f} GB"
    specs['Used Disk Space'] = f"{disk.used / (1024 ** 3):.2f} GB"
    specs['Free Disk Space'] = f"{disk.free / (1024 ** 3):.2f} GB"

    return specs

def specs_to_string(specs):
    return "\n".join([f"{key}: {value}" for key, value in specs.items()])
