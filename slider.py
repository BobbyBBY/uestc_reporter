from pymouse import *     # 模拟鼠标所使用的包
from pykeyboard import *   # 模拟键盘所使用的包
# pywin32 pyHook pyuserinput
import time   # 连续进行两个动作可能太快而效果不明显，因此加入暂停时间
import numpy as np
from PIL import ImageGrab
import random
from datetime import datetime, timedelta
import socket
import win32api, win32con
import sys
import traceback

def grab_screen(left,top,right,bottom):
    try:
        img = ImageGrab.grab(bbox=(1190, 520, 1400, 730))
    except Exception as e:
        pass
        # n_time = datetime.now()
        # print("img_grab_1")
        # print(n_time)
        # printError(e)
        # print("")
    try:
        img = ImageGrab.grabclipboard()
        for i in range(100):
            win32api.keybd_event(win32con.VK_SNAPSHOT, 0, 0, 0)
            time.sleep(0.2)
            win32api.keybd_event(win32con.VK_SNAPSHOT, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(2)
            img = ImageGrab.grabclipboard()
            if img is None:
                continue
            else:
                rect = (left, top, right, bottom)
                img = img.crop(rect)
                return img
    except Exception as e:
        n_time = datetime.now()
        print("img_grab_2")
        print(n_time)
        printError(e)
        print("")
    print("None")
    return None

def punch(flag=1):
    try:
        k = PyKeyboard()   # 键盘的实例
        m = PyMouse()   # 鼠标的实例
        # x_dim, y_dim = m.screen_size() # 获取屏幕尺寸
        print("创建键鼠实例")
        # m.click(280, 10, 1, 1) # 浏览器选项卡
        m.click(400, 1050, 1, 1) # 浏览器
        # time.sleep(1)
        # m.click(150, 120, 1, 1) # 新建隐私浏览器
        time.sleep(3)
        k.press_key(k.windows_l_key)
        time.sleep(0.1)
        k.tap_key(k.up_key)
        time.sleep(0.1)
        k.release_key(k.windows_l_key)
        time.sleep(1)
        k.type_string('eportal.uestc.edu.cn/new/index.html\n') # 模拟键盘输入字符串
        print("输入url")
        time.sleep(0.1)
        k.tap_key(k.enter_key)
        time.sleep(3) # 等待网页加载
        m.click(950, 620, 1, 1) # 登录按钮
        time.sleep(3) # 等待网页加载
        m.click(1500, 400, 1, 1) # 用户名输入框
        time.sleep(1)
        if flag==1:
            m.click(1500, 440, 1, 1) # 自动填充
        else:
            m.click(1500, 510, 1, 1) # 自动填充
        print("自动填充")
        '''
        键盘抖动
        # k.type_string(username)
        # # k.tap_key(k.numpad_keys[2])
        # time.sleep(0.2)
        # k.tap_key(k.tab_key) # 点击tab键
        # time.sleep(0.2)
        # k.type_string(password)
        '''
        time.sleep(0.2)
        k.tap_key(k.enter_key)
        # m.move(1200, 480) # 登录按钮
        time.sleep(1) # 等待加载滑块验证码

        # 识别滑块位置
        # 滑块中点在【1140，1240】间
        # m.move(1140, 510) 
        # time.sleep(2)
        # m.move(1240, 510) 

        print("开始随机滑块")
        for i in range(100):
            # 通过背景检测是否进入门户系统
            # img = ImageGrab.grab(bbox=(250,400,300,450)) # 大图
            img = grab_screen(250,400,300,450)
            img = np.array(img.getdata(), np.uint8).reshape(img.size[1], img.size[0], 3)
            flag = True
            for i in range(50):
                for j in range(50):
                    flag = flag and ((img[i][j][0] < 110) and (img[i][j][1] < 200))
            if not flag :
                break

            # 随机滑块位置
            det_x = random.randint(0,140)
            m.press(1400, 550, 1) # 滑块起始位置
            # time.sleep(0.1) # 稍微等待动画效果，可以不等
            # m.move(1170, 510) # 滑块终止位置
            # time.sleep(0.1) # 稍微等待动画效果，可以不等
            m.release(1430+det_x, 550, 1) # 滑块终止位置
            time.sleep(4)
        print("随机滑块成功")
        time.sleep(3)
        m.click(1600, 280, 1, 1) # 健康打卡
        time.sleep(5)
        m.click(1400, 120, 1, 1) # 体温上报
        time.sleep(3)
        print("健康打卡")

        m.click(190, 340, 1, 1) # 新增
        time.sleep(3)
        m.click(350, 520, 1, 1) # 时间
        time.sleep(1)
        m.click(350, 610, 1, 1) # 时间 上午
        time.sleep(1)
        m.click(350, 560, 1, 2) # 温度
        time.sleep(1)
        k.type_string('37')
        m.click(180, 970, 1, 1) # 保存
        time.sleep(1)
        m.click(1100, 620, 1, 1) # comfirm
        time.sleep(3)
        print("上午体温")

        m.click(190, 340, 1, 1) # 新增
        time.sleep(3)
        m.click(350, 520, 1, 1) # 时间
        time.sleep(1)
        m.click(350, 640, 1, 1) # 时间 中午
        time.sleep(1)
        m.click(350, 560, 1, 2) # 温度
        time.sleep(1)
        k.type_string('37')
        m.click(180, 970, 1, 1) # 保存
        time.sleep(1)
        m.click(1100, 620, 1, 1) # comfirm
        time.sleep(3)
        print("中午体温")

        m.click(190, 340, 1, 1) # 新增
        time.sleep(3)
        m.click(350, 520, 1, 1) # 时间
        time.sleep(1)
        m.click(350, 670, 1, 1) # 时间 晚上
        time.sleep(1)
        m.click(350, 560, 1, 2) # 温度
        time.sleep(1)
        k.type_string('37')
        m.click(180, 970, 1, 1) # 保存
        time.sleep(1)
        m.click(1100, 620, 1, 1) # comfirm
        time.sleep(3)
        print("晚上体温")

        m.click(1300, 120, 1, 1) # 每日报平安
        time.sleep(4)
        m.click(190, 270, 1, 1) # 新增
        time.sleep(3)
        m.click(180, 970, 1, 1) # save
        time.sleep(2)
        m.click(1000, 620, 1, 1) # comfirm
        time.sleep(3)
        print("每日平安")

        m.click(100, 20, 1, 1) # 门户选项卡
        time.sleep(2)
        m.click(1850, 120, 1, 1) # 用户
        time.sleep(1)
        m.click(1800, 270, 1, 1) # 退出
        time.sleep(1)
        print("退出")

        m.click(1900, 20, 1, 1) # 关闭浏览器
        print("关闭浏览器")
    except Exception as e:
        n_time = datetime.now()
        print("punch")
        print(n_time)
        printError(e)
        print("")

def connect():
    try:
        k = PyKeyboard()   # 键盘的实例
        m = PyMouse()   # 鼠标的实例
        m.click(400, 1050, 1, 1) # 浏览器
        time.sleep(3)
        k.press_key(k.windows_l_key)
        time.sleep(0.1)
        k.tap_key(k.up_key)
        time.sleep(0.1)
        k.release_key(k.windows_l_key)
        time.sleep(1)
        k.type_string('10.253.0.235\n') # 模拟键盘输入字符串
        time.sleep(0.1)
        k.tap_key(k.enter_key)
        time.sleep(5) # 等待网页加载

        flag = True
        # img = ImageGrab.grab(bbox=(1190, 520, 1200, 530)) # 注销按钮
        img = grab_screen(1190, 520, 1200, 530)
        img = np.array(img.getdata(), np.uint8).reshape(img.size[1], img.size[0], 3)
        for i in range(10):
            for j in range(10):
                flag = flag and ((img[i][j][1] < 130) and (img[i][j][2] < 130) and (img[i][j][0] > 230))

        if flag:
            print("不知道发生什么了")
            m.click(1190, 520, 1, 1)
            time.sleep(2)
            # 登录
            m.click(1200, 430, 1, 1) # username
            time.sleep(1)
            m.click(1200, 470, 1, 1) # auto
            time.sleep(1)
            m.click(1350, 550, 1, 1) # tel login
            time.sleep(1)

            m.click(1900, 20, 1, 1) # 关闭浏览器
        else:
            # 登录
            m.click(1200, 430, 1, 1) # username
            time.sleep(1)
            m.click(1200, 470, 1, 1) # auto
            time.sleep(1)
            m.click(1350, 550, 1, 1) # tel login
            time.sleep(1)

            m.click(1900, 20, 1, 1) # 关闭浏览器
    except Exception as e:
        n_time = datetime.now()
        print("connect")
        print(n_time)
        printError(e)
        print("")

def isNetOK(testserver):
    s = socket.socket()
    s.settimeout(3)
    try:
        status = s.connect_ex(testserver)
        if status == 0:
            s.close()
            return True
        else:
            return False
    except Exception as e:
        n_time = datetime.now()
        print("isNetOK")
        print(n_time)
        printError(e)
        print("")
        return False

def printError(e):
    print('str(Exception):\t', str(Exception))
    print('str(e):\t\t', str(e))
    print('repr(e):\t', repr(e))
    # Get information about the exception that is currently being handled  
    exc_type, exc_value, exc_traceback = sys.exc_info() 
    print('e.type:\t', exc_type)
    print('e.message:\t', exc_value)
    print('e.traceback:\t', exc_traceback)
    print("Note, object e and exc of Class %s is %s the same." % 
            (type(exc_value), ('not', '')[exc_value is e]))
    print('traceback.print_exc(): ', traceback.print_exc())
    print('traceback.format_exc():\n%s' % traceback.format_exc())

add_days = 5
time.sleep(60*5)
while(True):
    try:
        isOK = isNetOK(('www.baidu.com',443))
        if not isOK:
            try:
                connect()
                print("connected")
                n_time = datetime.now()
                print(n_time)
            except Exception as e:
                print("connect error\n")
                n_time = datetime.now()
                print(n_time)
                printError(e)
        
        start_date_str = "2021-01-23-0" + str(6+random.randint(0,3)) + "-" + str(random.randint(10,59)) + "-" + str(random.randint(10,59))
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d-%H-%M-%S") 
        offset = timedelta(days=add_days)
        start_date += offset
        n_time = datetime.now()
        if n_time > start_date:
            punch(1)
            punch(2)
            add_days += 1
        
        time.sleep(60*5)
    except Exception as e:
        print("main")
        n_time = datetime.now()
        print(n_time)
        print("")
        time.sleep(60*5)
        pass
