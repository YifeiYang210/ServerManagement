import datetime
import json
import platform
import psutil
import re
import requests
import socket

from flask import request, render_template

from config.config import visitDay
from index import app, sql
from lib.writeRes import writeResTask
from .login import cklogin

# 获取网关信息
NAThost = '未获取'
netIP = '未获取'
PCname = socket.gethostname()
try:
    ipContent = requests.get('http://pv.sohu.com/cityjson?ie=utf-8').text
    # var returnCitySN = {"cip": "xx.xx.xx.xx", "cid": "310000", "cname": "上海市"}; 公网IP
    ipContentJson = json.loads('{' + re.findall(r'{(.+?)}', ipContent)[0] + "}")
    # {"cip": "xx.xx.xx.xx", "cid": "310000", "cname": "上海市"}
    netIP = ipContentJson.get('cip')
except:
    pass
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    NAThost = s.getsockname()[0]
    # '172.24.15.90' 私网IP
except:
    pass
finally:
    s.close()
ResTask = writeResTask()
visitDay = visitDay


@app.route('/ControlPanel', methods=['POST', 'GET'])
@cklogin()
def ControlPanel():
    if request.method == 'GET':
        return render_template('ControlPanel.html',
                               inv=ResTask.inv,  # 间隔x秒
                               saveDay=ResTask.saveDay,  # 保存x天
                               state=('checked=""' if ResTask.state else ''),  # 是否显示
                               visitDay=visitDay,  # 显示x天
                               platform=platform.platform(),  # 系统名称：win10XXX
                               NETHOST=netIP,  # 外网IP
                               NATHOST=NAThost,  # 内网IP
                               PCname=PCname,  # 电脑名字
                               bootTime=datetime.datetime.fromtimestamp(psutil.boot_time()).strftime(
                                   "%Y-%m-%d,%H:%M:%S")  # 开机时间
                               )
    sqlResult = sql.selectInfo(day=visitDay)
    if not sqlResult[0]:
        return json.dumps({'resultCode': 1, 'result': sqlResult[1]})
    return json.dumps({'resultCode': 0, 'result': sqlResult[1]})


@app.route('/ControlPanelConfig', methods=['POST'])
@cklogin()
def ControlPanelConfig():
    state = request.values.get('state')
    saveDay = request.values.get('saveDay')
    inv = request.values.get('inv')
    reqVisitDay = request.values.get('visitDay')
    if reqVisitDay:
        reqVisitDay = int(reqVisitDay)
        if reqVisitDay < 1:
            return json.dumps({'resultCode': 1, 'result': '最少查看1天'})
        global visitDay
        visitDay = reqVisitDay
    if inv:
        inv = int(inv)
        if inv < 1:
            return json.dumps({'resultCode': 1, 'result': '最少间隔1秒'})
        ResTask.inv = inv
    if saveDay:
        saveDay = int(saveDay)
        if saveDay < 1:
            return json.dumps({'resultCode': 1, 'result': '最少储存一天,或者您可以选择关闭此功能'})
        ResTask.saveDay = saveDay
    ResTask.state = (True if (state == 'on') or (state == 'true') else False)
    return json.dumps({'resultCode': 0, 'result': 'success'})
