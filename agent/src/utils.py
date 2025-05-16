import psutil
import time
import socket
import platform
import uuid
import hashlib


def get_process_stats():
    # Step 1: Prime all processes
    procs = []
    for proc in psutil.process_iter(['pid', 'ppid', 'name']):
        try:
            proc.cpu_percent(interval=None)  # prime it
            procs.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # Step 2: Wait a short interval
    time.sleep(0.5)  # use 1.0 for more accurate reading, but higher delay

    # Step 3: Get actual CPU/memory usage
    process_data = []
    for proc in procs:
        try:
            cpu = proc.cpu_percent(interval=None)
            mem = proc.memory_info().rss / (1024 * 1024)  # memory in MB
            process_data.append({
                'pid': proc.pid,
                'ppid': proc.ppid(),
                'name': proc.name(),
                'cpu_usage': cpu,
                'memory_usage': mem,
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # Step 5: Get machine stats
    total_ram = psutil.virtual_memory().total
    available_ram = psutil.virtual_memory().available
    used_ram = total_ram - available_ram
    disk = psutil.disk_usage('/')
    machine_snapshot = {
        'total_ram': total_ram,
        'used_ram': used_ram,
        'available_ram': available_ram,
        'total_disk': disk.total,
        'used_disk': disk.used,
        'available_disk': disk.free
    }

    return {
        "machine_snapshot": machine_snapshot,
        "processes": process_data
    }

def get_machine_id():
    base = f"{platform.node()}-{uuid.getnode()}"
    return hashlib.sha256(base.encode()).hexdigest()

def get_machine_config():
    hostname = socket.gethostname()
    os_name = platform.system()
    processor = platform.processor()
    architecture = platform.machine()
    total_ram = psutil.virtual_memory().total
    core_count = psutil.cpu_count(logical=False)
    thread_count = psutil.cpu_count(logical=True)

    # Storage details
    disk = psutil.disk_usage('/')
    total_storage = disk.total

    return {
        "hostname": hostname,
        "os_name": os_name,
        "processor": processor,
        "architecture": architecture,
        "total_ram": total_ram,
        "cpu_cores": core_count,
        "cpu_threads": thread_count,
        "total_storage": total_storage,
        "machine_id": get_machine_id()
    }

if __name__ == "__main__":
    # Example usage
    print(get_process_stats())