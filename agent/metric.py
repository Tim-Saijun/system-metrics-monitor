import psutil
import GPUtil
import time
import requests
import json
from datetime import datetime
from config import CF_ACCOUNT_ID, CF_API_TOKEN, DATABASE_NAME, DEVICE_NAME

class NetworkSpeedMonitor:
    def __init__(self):
        self.prev_bytes_sent = psutil.net_io_counters().bytes_sent
        self.prev_bytes_recv = psutil.net_io_counters().bytes_recv
        self.prev_time = time.time()
        
    def get_speed(self):
        current_time = time.time()
        current_bytes_sent = psutil.net_io_counters().bytes_sent
        current_bytes_recv = psutil.net_io_counters().bytes_recv
        
        time_elapsed = current_time - self.prev_time
        
        upload_speed = (current_bytes_sent - self.prev_bytes_sent) / (time_elapsed + 0.00001) / (1024 )  # KB/s
        download_speed = (current_bytes_recv - self.prev_bytes_recv) / (time_elapsed + 0.0001) / (1024 )  # KB/s
        
        self.prev_bytes_sent = current_bytes_sent
        self.prev_bytes_recv = current_bytes_recv
        self.prev_time = current_time
        
        return {
            "upload_speed": round(upload_speed, 2),
            "download_speed": round(download_speed, 2)
        }
def get_cpu_usage():
    return psutil.cpu_percent(interval=1)
def get_memory_usage():
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return {
        "total": memory.total,
        "used": memory.used,
        "percent": memory.percent,
        "swap_total": swap.total,
        "swap_used": swap.used,
        "swap_percent": swap.percent
    }
    
def get_disk_usage():
    disk = psutil.disk_usage('/')
    return {
        "total": disk.total,
        "used": disk.used,
        "percent": disk.percent
    }
def get_gpu_metrics():
    try:
        gpus = GPUtil.getGPUs()
        if not gpus:
            return []
        
        gpu_metrics = []
        for i, gpu in enumerate(gpus):
            gpu_metrics.append({
                "gpu_index": i,
                "gpu_name": gpu.name,
                "gpu_load": gpu.load * 100,
                "gpu_memory_used": gpu.memoryUsed,
                "gpu_memory_total": gpu.memoryTotal,
                "gpu_temperature": gpu.temperature
            })
        return gpu_metrics
    except Exception as e:
        print(f"Failed to get GPU metrics: {e}")
        return []


network_monitor = NetworkSpeedMonitor()
def upload_to_d1(metrics):
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/d1/database/{DATABASE_NAME}/query"
    
    headers = {
        "Authorization": f"Bearer {CF_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # 插入主要系统指标
    main_sql = """
    INSERT INTO system_metrics (
        timestamp, device_name, cpu_percent, memory_total, memory_used, memory_percent,
        swap_total, swap_used, swap_percent, disk_total, disk_used,
        disk_percent, network_upload_speed, network_download_speed
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    RETURNING id;
    """
    
    main_params = [
        datetime.now().isoformat(),
        DEVICE_NAME,
        metrics['cpu']['percent'],
        metrics['memory']['total'],
        metrics['memory']['used'],
        metrics['memory']['percent'],
        metrics['memory']['swap_total'],
        metrics['memory']['swap_used'],
        metrics['memory']['swap_percent'],
        metrics['disk']['total'],
        metrics['disk']['used'],
        metrics['disk']['percent'],
        metrics['network']['upload_speed'],
        metrics['network']['download_speed']
    ]
    
    try:
        response = requests.post(url, headers=headers, json={"sql": main_sql, "params": main_params})
        response.raise_for_status()
    except Exception as e:
        print(response.json())
        print(f"Failed to upload main metrics: {e}")
        
    # 插入GPU指标
    if metrics['gpus']:
        gpu_sql = """
        INSERT INTO gpu_metrics (
            timestamp, device_name, gpu_index, gpu_name, gpu_load,
            gpu_memory_used, gpu_memory_total, gpu_temperature
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        for gpu in metrics['gpus']:
            gpu_params = [
                datetime.now().isoformat(),
                DEVICE_NAME,
                gpu['gpu_index'],
                gpu['gpu_name'],
                gpu['gpu_load'],
                gpu['gpu_memory_used'],
                gpu['gpu_memory_total'],
                gpu['gpu_temperature']
            ]
            try:
                response = requests.post(url, headers=headers, json={"sql": gpu_sql, "params": gpu_params})
                response.raise_for_status()
            except Exception as e:
                print(response.json())
                response.raise_for_status()
                print(f"Failed to upload GPU metrics: {e}")
                response.raise_for_status()
    
def collect_metrics():
    network_speeds = network_monitor.get_speed()
    
    metrics = {
        "cpu": {"percent": psutil.cpu_percent(interval=1)},
        "memory": {
            "total": psutil.virtual_memory().total,
            "used": psutil.virtual_memory().used,
            "percent": psutil.virtual_memory().percent,
            "swap_total": psutil.swap_memory().total,
            "swap_used": psutil.swap_memory().used,
            "swap_percent": psutil.swap_memory().percent
        },
        "disk": {
            "total": psutil.disk_usage('/').total,
            "used": psutil.disk_usage('/').used,
            "percent": psutil.disk_usage('/').percent
        },
        "network": network_speeds,
        "gpus": get_gpu_metrics()
    }
    return metrics


if __name__ == "__main__":
    network_monitor = NetworkSpeedMonitor()
    
    while True:
        try:
            metrics = collect_metrics()
            upload_to_d1(metrics)
            # print(json.dumps(metrics, indent=2))
            print("数据上传成功" + datetime.now().isoformat())
            time.sleep(60)
        except Exception as e:
            print(f"发生错误: {e}")
            time.sleep(60)
            