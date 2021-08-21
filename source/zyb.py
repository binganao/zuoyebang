import requests
import re
import time
import hashlib
from datetime import datetime
import yaml
import os
import json
import platform

login_url = "https://wenda.zuoyebang.com/commitui/session/login" # 获取token的地址
task1_url = "https://wenda.zuoyebang.com/rui/ask/taskpool" # 获取题目池
do_task_url = "https://wenda.zuoyebang.com/commitui/question/getitem" # 抢题地址

# GLOBAL SIMBOL
VERSION = "1.12.5"
TIME_SLEEP = 0.15 # 刷新题池的间隔
user_name = "" # 初始化 user_name 
user_pwd = "" # 初始化 user_pwd 
do_flag = False # 抢到题就结束循环
i = 1 # 计数
get_time = datetime.now() # 计算开始时间
reget_time = datetime.now() # 计算结束时间
FUCK_TIME = 0 # 用户配置的两次抢题的间隔阈值
FUCK_INTERVAL = 0.4 # 抢题阈值
DISPLAY_FUCK_TIME = 0 # 用于显示的FUCK_TIME
info_time = 1.5
DEBUG = False
TASKPOOL = 0
# GLOBAL SIMBOL

# REQUESTS
req = requests.session()
req.keep_alive = False
# REQUESTS

# 应对pwd参数的二重加密
def md5(s):
    m = hashlib.md5(s.encode())
    return(m.hexdigest())

# 程序初始化
def init():
    # 加载 user.yml 的用户名和密码
    USER_INFO = []
    with open("./user.yml",encoding="utf-8") as f:
        global user_name,user_pwd,DEBUG,FUCK_TIME,DISPLAY_FUCK_TIME,TASKPOOL
        try:
            USER_INFO = yaml.safe_load(f)
            user_name = USER_INFO['username']
            user_pwd = md5(md5(USER_INFO['password']))
            DEBUG = USER_INFO['debug']
            FUCK_TIME = int(USER_INFO['interval']) / 1000
            DISPLAY_FUCK_TIME = FUCK_TIME
            FUCK_TIME = FUCK_TIME + FUCK_INTERVAL
            TASKPOOL = int(USER_INFO['taskpool'])
        except:
            print('请修改「user.yml」内容')
            time.sleep(info_time)
            exit(0)
    if(not (TASKPOOL == 1 or TASKPOOL == 2 or TASKPOOL == 3)):
        print("请选择想要抢题的目标：\n  1 - 学生任务和平台任务\n  2 - 仅学生任务\n  3 - 仅平台任务")
        try:
            TASKPOOL = int(input("请输入："))
            with open("./user.yml",'w',encoding="utf-8") as f:
                USER_INFO['taskpool'] = TASKPOOL
                # f.write(USER_INFO)
                yaml.dump(USER_INFO,f)
        except KeyboardInterrupt:
            exit()
        except:
            print("你的输入有误，请重新输入")
            init()
    # print(TASKPOOL)
    time.sleep(1)
    if(not (TASKPOOL == 1 or TASKPOOL == 2 or TASKPOOL == 3)):
        print("你的输入有误，请重新输入")
        init()

# 获取教师的 token 并且显示用户信息
def get_token():
    # 传入登录接口的参数
    login_datas = {
        'code':'093phMkl2OLEF649lcll20v8fk2phMkU',
        'userName':user_name,
        'pwd':user_pwd,
        'fromChannel':'wechat',
        'token':'8ca6949132a5ec2715c924af244fef3aee0ee8fc',
        'mpversion':'202012291627'
    }
    # requests 和 re 获取token的值
    request = req.post(login_url,data=login_datas)
    re_temp = re.compile(r'en":"(.*?)"},"lo')
    global user_token
    try:
        user_token = re_temp.findall(request.text)[0]
    except:
        print('用户名或密码错误...程序终止')
        time.sleep(info_time)
        exit(0)

    print("当前版本："+VERSION)
    if(TASKPOOL == 1):
        print("抢题目标：" + "「学生任务和平台任务」")
    if(TASKPOOL == 2):
        print("抢题目标：" + "「仅学生任务」")
    if(TASKPOOL == 3):
        print("抢题目标：" + "「仅平台任务」")
    print("抢题间隔：" + str(int((DISPLAY_FUCK_TIME) * 1000)) + " ms")
    if DEBUG == True:
        print("当前登录用户："+user_name+"\n教师Token："+user_token)
        alog("\nget_token: \n"+request.text)
    else:
        lens = len(user_name)
        print("您已经登录："+user_name[0:3]+"*"*(lens-3)+user_name[lens-3:])


# 获取题池内可以抢题的数量
def do_task_pool(taskpool_id):
    global i
    global get_time
    global reget_time
    global do_flag
    task_datas = {
        'taskFrom':str(taskpool_id),
        'token':user_token
    }
    request = req.post(task1_url,data=task_datas,timeout=200)
    res_t = request.text
    if DEBUG == True:
        alog("\n"+request.text)
    re_temp1 = re.compile(r'"errNo":(.*?),"er')
    # print(res_t)
    
    print("\r> 请求次数：" + str(i) + " 次", end='', flush=True)
    if(int(re_temp1.findall(res_t)[0])==0):
        # 判断题目总量是否大于等于1，若大于则抢题
        re_temp2 = re.compile(r'tal":(.*?),"cou')
        total = re_temp2.findall(res_t)[0]
        # print(total)
        if(int(total)>=1):
            reget_time = datetime.now()
            # 加入频繁抢题检测
            if((int(reget_time.strftime('%S'))*1000000+int(reget_time.strftime('%f'))-int(get_time.strftime('%S'))*1000000-int(get_time.strftime('%f')))/1000000>=FUCK_TIME):
                fuck_task(str(taskpool_id))
                get_time = reget_time
    elif(int(re_temp1.findall(res_t)[0])==3):
        print("\n[BAD] Token过期，请重新运行程序，得到新的Token")
        time.sleep(info_time)
        exit(0)
    elif(int(re_temp1.findall(res_t)[0])==300010):
        # 频繁请求 忽视
        pass
    else:
        print(res_t)
    
    time.sleep(TIME_SLEEP)
    i = i+1

# 选择题池抢题
def do_task_list():
    if DEBUG == True:
            alog("\n"+"task_list: ")
    while(not do_flag):
        if(TASKPOOL == 1):
            do_task_pool(1)
            do_task_pool(2)
        if(TASKPOOL == 2):
            do_task_pool(1)
        if(TASKPOOL == 3):
            do_task_pool(2)

# 抢题
def fuck_task(s):
    if DEBUG == True:
            alog("\n"+"fuck_task: ")
    global do_flag
    # 抢题所用到的请求参数值
    do_datas={
        'businessId':hashlib.md5(str(time.time()).encode(encoding='UTF-8')).hexdigest(),
        'ts':'1615569262',
        'sign':'',
        'ticket':'',
        'randStr':'',
        'taskFrom':s,
        'token':user_token
    }
    request = req.post(do_task_url,data=do_datas)
    res_t = request.text
    if DEBUG == True:
        alog("\n"+request.text)
    # print(res_t)
    re_temp = re.compile(r'"errNo":(.*?),"err')
    errNo = int(re_temp.findall(res_t)[0])
    print(' => 当前有题可抢,',end='',flush=True)
    # 判断是否抢题成功
    if(errNo == 9001):
        clear()
        print("抢题速度过快，请适当修改user.yml文件中interval的值建议每次增加100\n在此之前，你需要「手动抢一道题」以继续使用本脚本")
        time.sleep(3600)
        exit(0)
    if(errNo == 0):
        print("尝试抢题...抢题成功！",end='',flush=True)
        print('\a')
        time.sleep(info_time)
        do_flag = True
        exit(0)
    # 抢题失败的操作
    elif(errNo==5002):
        print("尝试抢题...你还没做完当前的题目？！",end='',flush=True)
        time.sleep(info_time)
        do_flag = True
        exit(0)
    else:
        print("尝试抢题...抢题失败",end='',flush=True)


def main():
    # 程序执行流程
    clear()
    try:
        api_r = requests.post("http://localhost/update.php",timeout=200)
    except:
        print('检查更新失败，联系饼干获取修复版本')
        exit(0)
    if api_r.status_code != 200:
        print('检查更新失败，联系饼干获取修复版本')
        exit(0)
    api = json.loads(api_r.text)
    if VERSION != api['version']:
        print(api['upload_message'])
        if('download' in api):
            if(api['download'] != "NULL"):
                print("正在为您下载新版本更新包，请勿关闭程序")
                dl = requests.get(api['download']).content
                with open(api['version']+".zip", "wb") as update_file:
                    update_file.write(dl)
                    print("更新完成！")
                    time.sleep(info_time)
                    exit(0)
        time.sleep(3600)
        exit(0)
    print(api['message'])
    if DEBUG == True:
        print('「当前为DEBUG模式，正常使用无需启用！」')
    time.sleep(0.5)
    global do_flag
    do_flag = False
    global i
    i = 1
    # clear()
    starttime = datetime.now()
    get_token()
    do_task_list()

# 清空
def clear():
    if platform.system().lower() == 'windows':
        os.system('cls')
    else:
        os.system('clear')

# debug的log文件
def alog(message):
    with open(str(datetime.now().year) + "-" + str(datetime.now().month) + "-" + str(datetime.now().day) + ".log","a+") as log:
        log.write(message)
        log.close()

if __name__ == "__main__":
    try:
        init()
        main()
    except KeyboardInterrupt:
        print("\n程序退出！")
        time.sleep(info_time)
        exit(0)
