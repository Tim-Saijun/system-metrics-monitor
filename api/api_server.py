
# Cloudflare配置
CF_ACCOUNT_ID = "your_account_id"
CF_API_TOKEN = "your_api_token"
DATABASE_NAME = "your_database_name"

from flask import Flask, jsonify
import requests
from datetime import datetime, timedelta
from flask_caching import Cache
from prometheus_client import Counter, Histogram
import time
app = Flask(__name__)
cache = Cache(config={'CACHE_TYPE': 'simple'})
cache.init_app(app)
request_count = Counter('api_requests_total', 'Total API requests')
request_latency = Histogram('api_request_latency_seconds', 'API request latency')
@app.route('/api/metrics')
@cache.cached(timeout=60)
@request_latency.time()
def get_metrics():
    request_count.inc()
    
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/d1/database/{DATABASE_NAME}/query"
    headers = {
        "Authorization": f"Bearer {CF_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    time_ago = (datetime.now() - timedelta(hours=24)).isoformat()
    
    query = """
    SELECT 
        strftime('%Y-%m-%d %H:%M', timestamp) as time_bucket,
        AVG(cpu_percent) as cpu_avg,
        MAX(cpu_percent) as cpu_max,
        AVG(memory_percent) as memory_avg,
        AVG(swap_percent) as swap_avg,
        AVG(disk_percent) as disk_avg,
        AVG(gpu_load) as gpu_load_avg,
        AVG(gpu_temperature) as gpu_temp_avg,
        AVG(network_upload_speed) as upload_speed_avg,
        AVG(network_download_speed) as download_speed_avg
    FROM system_metrics
    WHERE timestamp > ?
    GROUP BY time_bucket
    ORDER BY time_bucket DESC
    """
    
    data = {
        "sql": query,
        "params": [time_ago]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)