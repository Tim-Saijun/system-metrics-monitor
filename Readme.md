
### Cloudflare Worker 配置

1. **创建 Cloudflare Worker**

   - 登录到 [Cloudflare Dashboard](https://dash.cloudflare.com/)
   - 选择你的账户和站点
   - 在左侧菜单中选择 "Workers" -> "Create a Service"
   - 输入服务名称并选择 "HTTP handler"
   - 点击 "Create service"

2. **部署 Worker 代码**

   - 在 Worker 编辑器中，替换默认代码为上面的修正代码
   - 点击 "Save and Deploy"

3. **配置 D1 数据库**

   - 在 Cloudflare Dashboard 中，选择 "D1" -> "Create Database"
   - 创建数据库并记下数据库名称
   - 在 Worker 的环境变量中添加数据库绑定
     - 在 Worker 服务页面，选择 "Settings" -> "Variables"
     - 添加新的绑定，类型选择 "D1 Database"，名称为 `DB`，选择刚刚创建的数据库

4. **测试 API**

   - 访问 Worker 的 URL，例如 `https://your-worker.workers.dev/api/system_metrics?from=1704038399999&to=1904038399999`
   - 确认返回的数据正确

这样，你的 Cloudflare Worker 就配置完成了，可以通过 API 获取 `system_metrics` 和 `gpu_metrics` 数据。

### Grafana 配置

## 运行

```bash
pip3 install psutil GPUtil requests
nohup python3 ~/metric_monitor.py > ~/metric_monitor.log 2>&1 &
```

为了确保脚本在系统重启后继续运行，你可以使用 `cron` 作业来设置一个定时任务。以下是具体步骤：

1. 打开终端。
2. 编辑 `cron` 作业：

```sh
crontab -e
```

3. 在 `crontab` 文件中添加以下行，以便在每次系统启动时运行你的脚本：

```sh
@reboot nohup python3 ~/metric_monitor.py > ~/metric_monitor.log 2>&1 &
```

保存并退出编辑器。这样，每次系统启动时，`metric_monitor.py` 脚本都会自动运行，并且不会因为意外关机而中断。



## 在Windows上运行
要在Windows系统中设置一个任务，使得每次开机后每隔一分钟运行`metric_monitor.py`脚本，以下是具体步骤：

### 1. 准备Python脚本
确保你的`metric_monitor.py`已经准备好（开头位置的配置填写），并且你已经安装了Python环境和依赖。记下Python程序（安装依赖所对应的那个环境）的完整路径。将python路径`pythonw.exe`和脚本路径填入`metric_monitor.vbs`文件中。
记录下vbs文件的路径。

### 2. 打开任务计划程序
- 按 `Win + S` 键打开搜索框，输入“任务计划程序”，然后选择“任务计划程序”应用打开它。

### 3. 创建基本任务
- 在任务计划程序窗口的右侧操作面板中，点击“创建基本任务...”。
- 输入任务名称和描述（可选），例如命名为“RunPythonScriptEveryMinute”，然后点击“下一步”。

### 4. 设置触发器
- 选择“每天的某个时间”，然后点击“下一步”。

### 5. 设置操作
- 选择“启动程序”，然后点击“下一步”。
- 在“程序或脚本”栏中，浏览并选择第1步中vbs文件的路径。

### 6. 设置高级属性
- 完成上述步骤后，点击“完成”。此时，任务已经创建完毕，但是我们需要进一步配置它来实现每分钟运行一次。
- 在任务列表中找到你刚刚创建的任务，右键点击它，选择“属性”。
- 切换到“触发器”选项卡，选中你创建的触发器，然后点击下方的“编辑”按钮。
- 在“高级设置”区域勾选“重复任务间隔”选项，并设置为“1分钟”，然后选择“持续时间”为“直到任务完成”或一个足够长的时间段。
- 确认所有设置无误后，点击“确定”保存更改。

### 7. 测试任务
- 为了确保任务可以正常工作，你可以尝试手动运行这个任务，检查Python脚本是否按照预期执行。
- 在任务计划程序中，找到你的任务，右键点击它，选择“运行”。
