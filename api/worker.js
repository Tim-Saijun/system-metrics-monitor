export default {
  async fetch(request, env) {
    const url = new URL(request.url)
    const path = url.pathname
    
    // 允许跨域
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET,OPTIONS',
      'Access-Control-Allow-Headers': '*',
      'Content-Type': 'application/json'
    }

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders })
    }

    // 添加x-api-key验证
    const apiKey = request.headers.get('x-api-key')
    if (!apiKey || apiKey !== env.API_TOKEN) {
      return new Response('Unauthorized', {
        status: 401,
        headers: corsHeaders
      })
    }

    try {
      let result
      const params = Object.fromEntries(url.searchParams)
      const { from, to, device_name } = params

      if (!from || !to) {
        return new Response(JSON.stringify({ error: "Missing 'from' or 'to' query parameters" }), {
          status: 400,
          headers: corsHeaders
        })
      }

      // 解析时间参数，添加8小时偏移
      const fromDate = new Date(parseInt(from) + 8 * 60 * 60 * 1000).toISOString()
      const toDate = new Date(parseInt(to) + 8 * 60 * 60 * 1000).toISOString()

      switch (path) {
        case '/api/system_metrics':
          let systemQuery = `
            SELECT timestamp, device_name, 
                   cpu_percent, memory_percent, swap_percent, disk_percent,
                   memory_used, memory_total,
                   swap_used, swap_total,
                   disk_used, disk_total,
                   network_upload_speed, network_download_speed
            FROM system_metrics
            WHERE timestamp BETWEEN ? AND ?
          `
          const systemParams = [fromDate, toDate]
          
          if (device_name) {
            systemQuery += ' AND device_name = ?'
            systemParams.push(device_name)
          }
          
          systemQuery += ' ORDER BY timestamp'
          result = await env.DB.prepare(systemQuery).bind(...systemParams).all()
          break

        case '/api/gpu_metrics':
          let gpuQuery = `
            SELECT timestamp, device_name, gpu_index,
                   gpu_name, gpu_load, gpu_memory_used,
                   gpu_memory_total, gpu_temperature
            FROM gpu_metrics
            WHERE timestamp BETWEEN ? AND ?
          `
          const gpuParams = [fromDate, toDate]

          if (device_name) {
            gpuQuery += ' AND device_name = ?'
            gpuParams.push(device_name)
          } else {
            gpuQuery += ' AND gpu_index = 0'
          }

          gpuQuery += ' ORDER BY timestamp'
          result = await env.DB.prepare(gpuQuery).bind(...gpuParams).all()
          break

        default:
          return new Response('Not Found', { status: 404 })
      }

      return new Response(JSON.stringify(result.results), {
        headers: corsHeaders
      })
      
    } catch (err) {
      return new Response(JSON.stringify({ error: err.message }), {
        status: 500,
        headers: corsHeaders
      })
    }
  }
}