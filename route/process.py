import psutil
from flask import request, render_template, redirect, send_file, send_from_directory, url_for, session, make_response
from index import app, url
import json
import platform, os, datetime, sys
from .login import cklogin
import zipfile, time, os
import random

url.append({
    "title": "进程监控",
    "href": "/Process",
})
wink = ['SYSTEM', 'SYSTEMIDLEPROCESS', 'SMSS.EXE',
        'CSRSS.EXE', 'WININIT.EXE', 'WINLOGON.EXE', 'SERVICES.EXE',
        'LSASS.EXE', 'SVCHOST.EXE', 'DWM.EXE', 'MEMORYCOMPRESSION',
        'TASKHOSTW.EXE', 'RUNTIMEBROKER.EXE', 'EXPLORER.EXE', 'SHELLEXPERIENCEHOST.EXE',
        'APPLICATIONFRAMEHOST.EXE', 'SYSTEMSETTINGS.EXE', 'WMIPRVSE.EXE', 'PLUGIN_HOST.EXE',
        'SPOOLSV.EXE', 'DASHOST.EXE', 'SIHOST.EXE', 'CONHOST.EXE', 'DLLHOST.EXE', 'TASKLIST.EXE',
        'NVCONTAINER.EXE', 'SEARCHUI.EXE', 'REGISTRY', 'FONTDRVHOST.EXE', 'IGFXCUISERVICE.EXE',
        'NVTELEMETRYCONTAINER.EXE', 'SECURITYHEALTHSERVICE.EXE', 'PRESENTATIONFONTCACHE.EXE',
        'SEARCHINDEXER.EXE', 'IGFXEM.EXE', 'IGFXHK.EXE', 'CTFMON.EXE', 'SMARTSCREEN.EXE', 'CTFMON.EXE',
        'SETTINGSYNCHOST.EXE', 'WINDOWSINTERNAL.COMPOSABLESHELL.EXPERIENCES.TEXTINPUT.INPUTAPP.EXE',
        'CHSIME.EXE', 'AUDIODG.EXE', 'USYSDIAG.EXE', 'SEARCHPROTOCOLHOST.EXE', 'SEARCHFILTERHOST.EXE']

ps = ['SFTP-SERVER', 'LOGIN', 'NM-DISPATCHER', 'IRQBALANCE', 'QMGR', 'WPA_SUPPLICANT',
      'LVMETAD', 'AUDITD', 'MASTER', 'DBUS-DAEMON', 'TAPDISK', 'SSHD', 'INIT', 'KSOFTIRQD',
      'KWORKER', 'KMPATHD', 'KMPATH_HANDLERD', 'PYTHON', 'KDMFLUSH', 'BIOSET', 'CROND', 'KTHREADD',
      'MIGRATION', 'RCU_SCHED', 'KJOURNALD', 'IPTABLES', 'SYSTEMD', 'NETWORK', 'DHCLIENT',
      'SYSTEMD-JOURNALD', 'NETWORKMANAGER', 'SYSTEMD-LOGIND', 'SYSTEMD-UDEVD', 'POLKITD', 'TUNED', 'RSYSLOGD',
      'BASH', 'YDSERVICE', 'SYSTEMD']

netkey = {
    'SYN_SENT': '请求',
    'LISTEN': '监听',
    'ESTABLISHED': '已建立',
    'NONE': '未知',
    'CLOSE_WAIT': '中断',
    'LAST_ACK': '等待关闭'
}


# 进程视图
@app.route('/Process', methods=['GET', 'POST'])
@cklogin()
def Process():
    return render_template('Process.html')


# 取网络连接列表
# https://mp.weixin.qq.com/s?__biz=MzI4MzM2MDgyMQ==&mid=2247489291&idx=1&sn=4f15a6569144b87d7cf89cee785295c7&chksm=eb8abc51dcfd354758e781c3f83f086e33130553699be6ce0ae963c0663c047a65a229f6ef19&token=49216468&lang=zh_CN#rd
@app.route('/GetNetWorkList', methods=['POST', 'GET'])
@cklogin()
def GetNetWorkList():
    netstats = psutil.net_connections()  # 获取全部网络连接信息
    networkList = []
    for netstat in netstats:
        try:
            if (netstat.pid == 0) or not netstat.pid:
                continue
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
            tmp['process'] = tmp_name  # 程序文件名
            tmp['pid'] = netstat.pid  # 进程pid号
            tmp['type'] = ('tcp' if netstat.type == 1 else 'udp')  # 套接字类型
            tmp['laddr'] = netstat.laddr  # 本地连接
            tmp['raddr'] = netstat.raddr or 'None'  # 远程连接
            tmp['status'] = netkey.get(netstat.status, netstat.status)  # 连接状态
            networkList.append(tmp)
            del (p)
            del (tmp)
        except:
            continue
    for i in os.listdir('temp'):
        try:
            os.remove(os.path.join('temp', i))
        except:
            continue
    t = os.path.join('temp', str(time.time() + random.random()) + '.zip')
    f = zipfile.ZipFile(t, 'w', zipfile.ZIP_DEFLATED)
    while networkList != []:
        jsonName = os.path.join('temp', str(time.time() + random.random()) + '.json')
        with open(jsonName, 'w') as j:
            j.write(json.dumps(networkList[:100]))
        networkList = networkList[100:]
        f.write(jsonName)
    f.close()
    response = make_response(send_from_directory(os.path.split(t)[0], os.path.split(t)[1], as_attachment=True))
    response.headers["Content-Disposition"] = "attachment; filename={}".format((t + '.zip').encode().decode('latin-1'))
    return response


# 取进程列表
@app.route('/GetProcessList', methods=['POST'])
@cklogin()
def GetProcessList():
    Pids = psutil.pids()
    processList = []
    for pid in Pids:
        try:
            tmp = {}
            p = psutil.Process(pid)
            tmp['name'] = p.name()  # 进程名称
            if platform.system().upper() == 'WINDOWS':
                if tmp['name'].upper().replace(' ', '') in wink:
                    continue
            else:
                if tmp['name'].upper() in ps:
                    continue
            tmp['pid'] = pid
            tmp['user'] = os.path.split(p.username())[1]  # 执行用户
            tmp['memory_percent'] = str(round(p.memory_percent(), 3)) + '%'  # 进程占用的内存比例
            processList.append(tmp)
            del (p)
            del (tmp)
        except:
            continue
    processList = sorted(processList, key=lambda x: x['memory_percent'], reverse=True)
    return json.dumps({'resultCode': 0, 'result': processList})


# 结束进程
@app.route('/KillPid', methods=['GET', 'POST'])
@cklogin()
def KillProcess():
    try:
        pid = request.values.get('pid')
        p = psutil.Process(int(pid))
        p.kill()
    except Exception as e:
        return json.dumps({'resultCode': 1, 'result': str(e)})
    else:
        return json.dumps({'resultCode': 0, 'result': 'success'})


# 查看进程详细信息
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
            'ProcessName': p.name(),
            'ProcessPath': n,
            'ProcessStatus': p.status(),
            'ProcessStartTime': datetime.datetime.fromtimestamp(p.create_time()).strftime("%Y-%m-%d %H:%M:%S"),
            'ProcessMemory': str(round(p.memory_percent(), 3)) + '%',
            'ProcessThreads': p.num_threads(),
            'ProcessCPU': str(p.cpu_percent(0.2)) + '%',
            'ProcessUser': p.username(),
            'ProcessReadCount': proIO.read_count,
            'ProcessWriteCount': proIO.write_count,
            'ProcessReadBytes': proIO.read_bytes,
            'ProcessWriteBytes': proIO.write_bytes
        }
    except Exception as e:
        return json.dumps({'resultCode': 1, 'result': str(e) + '可能是权限不足'})
    else:
        return json.dumps({'resultCode': 0, 'result': ProcessDict})
