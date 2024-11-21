import requests
import sys
from config import CF_ACCOUNT_ID, CF_API_TOKEN, DATABASE_NAME

def create_tables():
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/d1/database/{DATABASE_NAME}/query"
    
    headers = {
        "Authorization": f"Bearer {CF_API_TOKEN}",
        "Content-Type": "application/json"
    }

    # 创建主表
    create_metrics_table = """
    CREATE TABLE IF NOT EXISTS system_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        cpu_percent REAL,
        memory_total BIGINT,
        memory_used BIGINT,
        memory_percent REAL,
        swap_total BIGINT,
        swap_used BIGINT,
        swap_percent REAL,
        disk_total BIGINT,
        disk_used BIGINT,
        disk_percent REAL,
        network_upload_speed REAL,
        network_download_speed REAL
    );
    """

    # 创建GPU指标表
    create_gpu_metrics_table = """
    CREATE TABLE IF NOT EXISTS gpu_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        metrics_id INTEGER,
        gpu_index INTEGER,
        gpu_name TEXT,
        gpu_load REAL,
        gpu_memory_used REAL,
        gpu_memory_total REAL,
        gpu_temperature REAL,
        FOREIGN KEY (metrics_id) REFERENCES system_metrics(id)
    );
    """

    # 创建索引
    create_indexes = """
    CREATE INDEX IF NOT EXISTS idx_timestamp ON system_metrics(timestamp);
    CREATE INDEX IF NOT EXISTS idx_metrics_id ON gpu_metrics(metrics_id);
    """

    queries = [create_metrics_table, create_gpu_metrics_table, create_indexes]

    for query in queries:
        try:
            data = {
                "sql": query,
                "params": []
            }
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            print(f"执行SQL成功: {query[:50]}...")
        except Exception as e:
            print(f"执行SQL失败: {e}")
            sys.exit(1)

if __name__ == "__main__":
    create_tables()