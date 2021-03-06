## 学习笔记

本项目前端采用layui+jquery，后端采用python+flask完成。

### 1.项目架构

`static`和`templates`目录是默认配置，其中`static`用来存放静态资源，例如图片、js、css文件等。`templates`存放模板文件。网站逻辑基本在`index.py`文件中，命令行输入`python index.py`启动本网站。

`index.py`包括网站的路由信息，网关信息。

### 2.项目功能

#### 2.1 我们的实现

1.新增进程管理.

2.新增计划任务(使用datatime计算时间，threading.Timer定时执行).

3.新增了一个很low的webssh.

4.新增资源监控，可以记录指定时间内的资源使用情况

5.新增登陆验证,原本想存在数据库里的,写完了又觉得没必要,暂时放在config里了,等以后抽时间加个面板设置的功能吧

6.新增远程主机管理,多主机批量执行shell,支持设定以root身份执行shell(目前很简陋,后续会添加更多功能)

7.文件管理器批量操作时增加提示

8.加上了文件批量剪切和复制

9.压缩了后台传递进程信息的大小,消耗流量仅为原先的约1/6,且分段生成前端页面,前端内存占用大幅减少

10.新增了文件管理器的图片预览功能(预览时图片为预览图,原图请点击下载)

11.优化文件管理器跨文件夹操作,已选中文件可单独去除,选中文件的全路径记录在session中,可开多个页面分别操作

12.计划任务储存在数据库中,重启进程会自动加载(使用早期版本的同志们注意修改数据库哦)

13.新增快捷按钮功能,可以在面板上为你常用的shell命令创建一个"快捷方式",然后一键调用,命令执行前可以对shell做出修改

14.新增文件的快捷按钮,设定好常用的文件,一键打开修改

15.优化页面的错误提示

16.计划任务增加执行日志,将详细的执行情况储存在/lib/tasklog目录下

17.新增windows下的远程桌面,远程控制,仅在windows下可用

18.为没有外网IP的服务器新增内网穿透功能,在有外网IP的服务器中运行服务端后,修改本服务器管理工具的配置并打开开关即可,访问服务端的ip，可以查看管理平台。精力有限,正在完善中，未来会加入管理平台的在线检测，实时显示全部服务器状态等，敬请期待

19.新增linux下的软件管理,增加nginx一键安装,及配置/管理等

20.文件管理器提供文件分享功能,可自定义文件提取码等(类似一个简陋的网盘)

#### 2.2 老师要求

请设计一套系统，实现检测如下信息：
（1）系统 CPU 、内存硬盘利用率等基本信息；√：完美完成(进程监控：CPU,内存,磁盘)
（2）帐户策略、密码审计访问控制等信息； √：完美完成(SHELL：远程连接，多机密码管理)
（3）软件列表； √：完美完成(可用文件管理器，文件分享网盘，linux下的安装nginx配置管理)
（4）进程列表信息； √：完美完成(进程监控：进程列表)
（5）服务列表信息； √：完美完成(进程监控：网络连接)
（6）其他与系统安全相关的信息。 √：远程桌面，脚本计划任务等

#### 2.3项目数据库

### 3 项目功能

```python
# CPU信息
cpuUsed = psutil.cpu_percent(1)
# 内存信息
memoryInfo = psutil.virtual_memory()
memoryUsedSize = round(memoryInfo.used / (1024.0 * 1024.0 * 1024.0), 2)
memoryUsed = round(memoryUsedSize / memoryTotal, 2) * 100
# 网络io
net = psutil.net_io_counters()
bytesRcvd = (net.bytes_recv / 1024)
bytesSent = (net.bytes_sent / 1024)
time.sleep(1)
net = psutil.net_io_counters()
realTimeRcvd = round(((net.bytes_recv / 1024) - bytesRcvd), 2)
realTimeSent = round(((net.bytes_sent / 1024) - bytesSent), 2)
tim = time.strftime('%H:%M:%S', time.localtime())
realTimeInfo = {
    'cpu': {'cpuUsed': cpuUsed},
    'memory': {'memoryUsed': memoryUsed},
    'net': {'rcvd': realTimeRcvd, 'send': realTimeSent}
}
sql.insertInfo(info=realTimeInfo)
sql.deleteInfo(day=self.saveDay)
```

`<field-set>`

```html
<div class="admin-main" style="width:46%;float: left">
  <fieldset class="layui-elem-field">
    <legend><a style="color: white">全部网络连接&#8195;</a>
      <a class='layui-btn layui-btn-normal layui-btn-sm' onclick='refNet()'>刷新</a>
      <a style="clear: both;font-size: 8px;color: #A4A4A4">点击进程名查看更多</a>
    </legend>
    <div class="layui-field-box">
      <table class="site-table table-hover">
        <thead style="color: white">
          <tr><th>进程名</th><th>pid</th><th>类型</th>
          <th>状态</th><th>本地</th><th>远程</th></tr>
        </thead>
        <tbody id="networkdataList" style="color: white"></tbody>
      </table>
    </div>
  </fieldset>
</div>
```

获取全部网络连接信息

```python 
@app.route('/GetNetWorkList', methods=['POST', 'GET'])
@cklogin()
def GetNetWorkList():
    netstats = psutil.net_connections()  # 获取全部网络连接信息
    networkList = []
    for netstat in netstats:
        try:
            tmp = {}
            p = psutil.Process(netstat.pid)
            tmp_name = p.name()
            # 根据系统平台的不同，过滤系统进程
            if platform.system().upper() == 'WINDOWS':
                if tmp_name.upper().replace(' ', '') in wink:
                    continue
            else:
                if tmp_name.upper() in ps:
                    continue
            tmp['process'] = tmp_name                                   # 程序文件名
            tmp['pid'] = netstat.pid                                    # 进程pid号
            tmp['type'] = ('tcp' if netstat.type == 1 else 'udp')       # 套接字类型
            tmp['laddr'] = netstat.laddr                                # 本地连接
            tmp['raddr'] = netstat.raddr or 'None'                      # 远程连接
            tmp['status'] = netkey.get(netstat.status, netstat.status)  # 连接状态
            networkList.append(tmp)
        except:
            continue
    #...
    return response
```

获取进程连接全部信息

```python 
@app.route('/ProcessDetails', methods=['POST'])
@cklogin()
def ProcessDetails():
    try:
        pid = request.values.get('pid')
        p = psutil.Process(int(pid))
        try:
            n = p.exe()
        except:
            n = 'None'
        proIO = p.io_counters()
        ProcessDict = {
            'ProcessName': p.name(),                                   # 进程名字
            'ProcessPath': n,                                          # 进程路径
            'ProcessStatus': p.status(),                               # 进程创建日期
            'ProcessStartTime': datetime.datetime                      
                                        .fromtimestamp(p.create_time())
                                        .strftime("%Y-%m-%d %H:%M:%S"),
            'ProcessMemory': str(round(p.memory_percent(), 3)) + '%',  # 进程内存
            'ProcessThreads': p.num_threads(),                         # 进程线程
            'ProcessCPU': str(p.cpu_percent(0.2)) + '%',               # 进程CPU
            'ProcessUser': p.username(),                               # 进程用户名
            'ProcessReadCount': proIO.read_count,                      # 进程读取IO
            'ProcessWriteCount': proIO.write_count,                    # 进程写入IO
            'ProcessReadBytes': proIO.read_bytes,                      # 进程读取字节数
            'ProcessWriteBytes': proIO.write_bytes                     # 进程写入字节数
        }
    except Exception as e:
        return json.dumps({'resultCode': 1, 'result': str(e) + '可能是权限不足'})
    else:
        return json.dumps({'resultCode': 0, 'result': ProcessDict})
```







