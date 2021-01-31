import requests
from my_request import get_request
import json
import re
from datetime import datetime
import time
import pickle
import socket
import sys
import traceback

from push_server import push
from selenium import webdriver
from personal_info import server_url, webdriver_path, daily_report_data, temp_report_data, login_data

from apscheduler.schedulers.blocking import BlockingScheduler


headers = {
    "Cookie": ""
}


def cookies2str(cookies):
    cookie = [item["name"]+"="+item["value"] for item in cookies]
    cookiestr = ';'.join(item for item in cookie)
    return cookiestr


class Reportor(object):

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.host = "eportal.uestc.edu.cn"
        self.login_url = "http://eportal.uestc.edu.cn/jkdkapp/sys/lwReportEpidemicStu/index.do?#/dailyReport"
        self.wid_url = '/jkdkapp/sys/lwReportEpidemicStu/modules/dailyReport/getMyTodayReportWid.do?'
        self.daily_report_check_url = "/jkdkapp/sys/lwReportEpidemicStu/modules/dailyReport/getMyDailyReportDatas.do?"
        self.daily_report_save_url = "/jkdkapp/sys/lwReportEpidemicStu/modules/dailyReport/T_REPORT_EPIDEMIC_CHECKIN_YJS_SAVE.do?"
        self.temp_report_check_url = "/jkdkapp/sys/lwReportEpidemicStu/mobile/tempReport/getMyTempReportDatas.do?"
        self.temp_report_save_url = "/jkdkapp/sys/lwReportEpidemicStu/mobile/tempReport/T_REPORT_TEMPERATURE_YJS_SAVE.do?"
        
    def login(self):
        print("logging in...\r", end="")
        options = webdriver.firefox.options.Options()
        options.add_argument('--headless')  # 无窗口
        options.add_argument('--incognito')  # 无痕
        driver = webdriver.Firefox(executable_path=webdriver_path, options=options)
        def update_cookies():
            Cookies = driver.get_cookies()
            driver.quit()
            headers["Cookie"] = cookies2str(Cookies)
        def _login(i):
            print("第{}次尝试登录".format(i))
            js = """
                var casLoginForm = document.getElementById("casLoginForm");
                var username = document.getElementById("username");
                var password = document.getElementById("password");
                username.value = "{}"
                password.value = "{}"
                _etd2(password.value, document.getElementById("pwdDefaultEncryptSalt").value);
                casLoginForm.submit();
            """.format(self.username, self.password)
            '''
            这里直接绕过了滑块验证码，滑块验证码判定结果为bool型，位置在login-wisedu_v1.0.js第196行,
            或者function reValidateDeal内的ajax下。
            '''
            driver.execute_script(js)
            # time.sleep(10)
        def _check():
            """return 1 为检测登陆成功"""
            try:
                driver.find_element_by_xpath("/html/body/header/header[1]/div/div/div[4]/div[1]/img").click()
                time.sleep(2)
                username = driver.find_element_by_xpath('/html/body/div[5]/div[2]/div[1]').text
            except Exception:
                time.sleep(10)
                return 0
            else:
                print("登录账号 ： {}".format(username))
                update_cookies()
                return 1
        for i in range(10):  # 重复尝试登陆十次
            driver.get(self.login_url)
            time.sleep(3)
            if _check():
                return
            _login(i+1)
            if _check():
                return
        push("登陆失败，上服务器看看我觉得我还有救")
        # if server_url is not None:
        #     requests.get(url=server_url+f'?text=登陆失败，上服务器看看我觉得我还有救')
        raise RuntimeError("登录失败")

    def _daily_report(self, NEED_DATE, daily_report_data):
        # 获取WID
        wid_data = {
            'pageNumber': '1',
            'pageSize': '10',
            'USER_ID': daily_report_data["USER_ID"],
        }
        res = get_request(self.host, "POST", self.wid_url, wid_data, headers)
        if re.search("<title>统一身份认证</title>", res):
            raise RuntimeError("Cookie失效")
        elif re.search("<title>302 Found</title>", res):
            raise RuntimeError("Cookie失效") 
        try:
            wid_json_loads = json.loads(res)
            wid = wid_json_loads['datas']['getMyTodayReportWid']['rows'][0]['WID']
            daily_report_data['WID'] = wid
        except json.decoder.JSONDecodeError:
            print("json解析失败")
            return 1

        # check
        check_data = {
            'pageNumber': '1',
            'pageSize': '10',
            'USER_ID': daily_report_data["USER_ID"],
            'KSRQ': NEED_DATE,
            'JSRQ': NEED_DATE,
        }
        res = get_request(self.host, "POST", self.daily_report_check_url, check_data, headers)
        if re.search("<title>统一身份认证</title>", res):
            raise RuntimeError("Cookie失效")
        elif re.search("<title>302 Found</title>", res):
            raise RuntimeError("Cookie失效") 
        try:
            parsed_res = json.loads(res)
        except json.decoder.JSONDecodeError:
            print("json解析失败")
            return 1
        try:
            if parsed_res['datas']['getMyDailyReportDatas']['totalSize'] > 0:
                print("daily report has finished")
                return 0  # 打卡成功
        except KeyError:
            pass

        # save
        daily_report_data.update({
            "NEED_CHECKIN_DATE": NEED_DATE,
            "CZRQ": NEED_DATE+" 00:00:00",
        })
        res = get_request(self.host, "POST", self.daily_report_save_url, daily_report_data, headers)
        if re.search("<title>统一身份认证</title>", res):
            raise RuntimeError("Cookie失效")
        elif re.search("<title>302 Found</title>", res):
            raise RuntimeError("Cookie失效") 
        try:
            parsed_res = json.loads(res)
        except json.decoder.JSONDecodeError:
            print("json解析失败")
            return 1
        if parsed_res['code'] == '0' and parsed_res['datas']['T_REPORT_EPIDEMIC_CHECKIN_YJS_SAVE'] == 1:
            print("daily report sucessful")
            return 0  # 打卡成功
        else:
            print("打卡失败")
            return 1

    def _temp_report(self, NEED_DATE, DAY_TIME, temp_report_data):
        check_data = {
            "USER_ID": temp_report_data["USER_ID"],
            "NEED_DATE": NEED_DATE,
            "DAY_TIME": DAY_TIME,
        }
        res = get_request(self.host, "POST", self.temp_report_check_url, check_data, headers)
        if re.search("<title>统一身份认证</title>", res):
            raise RuntimeError("Cookie失效")
        elif re.search("<title>302 Found</title>", res):
            raise RuntimeError("Cookie失效") 
        if re.search('"NEED_DATE":"{}","DAY_TIME":"{}"'.format(NEED_DATE, DAY_TIME), res) is not None:
            print("temp report {} has finished".format(DAY_TIME))
            return int(DAY_TIME)

        # save
        DAY_TIME_DISPLAY = {
            "1": "早上",
            "2": "中午",
            "3": "晚上",
        }
        temp_report_data.update({
            "DAY_TIME": DAY_TIME,
            "DAY_TIME_DISPLAY": DAY_TIME_DISPLAY[DAY_TIME],
            "NEED_DATE": NEED_DATE,
        })

        res = get_request(self.host, "POST", self.temp_report_save_url, temp_report_data, headers)
        if re.search("<title>统一身份认证</title>", res):
            raise RuntimeError("Cookie失效")
        elif re.search("<title>302 Found</title>", res):
            raise RuntimeError("Cookie失效") 
        try:
            assert re.search(r'"T_REPORT_TEMPERATURE_YJS_SAVE":(?P<r_value>\d)', res)["r_value"] == '1'
            print("temp report {} sucessful".format(DAY_TIME))
            return int(DAY_TIME)  # 打卡成功
        except Exception:
            time.sleep(5)
            return 0

    def daily_report(self, NEED_DATE, daily_report_data):
        try:
            return self._daily_report(NEED_DATE, daily_report_data)
        except RuntimeError as e:
            # print(e)
            push(str(e)+"，上服务器看看我觉得我还有救")
            # if server_url is not None:
            #     requests.get(url=server_url+f'?text=str(e)，上服务器看看我还有救吗')
            exit(0)
        except Exception:
            return 1

    def temp_report(self, NEED_DATE, DAY_TIME, temp_report_data):
        try:
            return self._temp_report(NEED_DATE, DAY_TIME, temp_report_data)
        except RuntimeError as e:
            # print(e)
            push(str(e)+"，上服务器看看我觉得我还有救")
            # if server_url is not None:
            #     requests.get(url=server_url+f'?text=str(e)，上服务器看看我还有救吗')
            exit(0)
        except Exception:
            return 1

def daily_check(reportor, daily_report_data, temp_report_data, date_str=None):
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
        print("当前时间：" + str(datetime.now()))
    # 平安打卡
    while(reportor.daily_report(date_str, daily_report_data)):
        continue
    # 体温上报
    r_value_list = []
    for id in range(1, 4):
        while(id not in r_value_list):
            r_value_list.append(reportor.temp_report(date_str, str(id), temp_report_data))
    # 四项打卡全部完成
    print("{} day {} report complete!\n".format(daily_report_data["USER_NAME"], date_str))
    return date_str


def check_job(reportor, daily_report_data, temp_report_data):
    reportor.login()
    for id in range(len(daily_report_data)):
        date_str = daily_check(reportor, daily_report_data[id], temp_report_data[id])
    push(date_str + " 打卡完成")
    # if server_url is not None:
    #     requests.get(url=server_url+f'?text={date_str}打卡完成')

# 打印错误内容
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
    push(exc_value + "\n" + exc_value + "\n" + exc_traceback)

# 断网重连
class Connecter(object):

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.login_url = "http://10.253.0.235"
        
    def connect(self):
        try:
            print("disconnected logging in...\r", end="")
            options = webdriver.firefox.options.Options()
            options.add_argument('--headless')  # 无窗口
            options.add_argument('--incognito')  # 无痕
            driver = webdriver.Firefox(executable_path=webdriver_path, options=options)
            driver.get(self.login_url)
            time.sleep(10)
            try:
                driver.find_element_by_id("ctcc-login")
                driver.find_element_by_id("username").send_keys(self.username)
                driver.find_element_by_id("password").send_keys(self.password)
                driver.find_element_by_id("ctcc-login").click()
                return
            except Exception as e:
                print("似乎已经登录了")
                pass
            try:
                driver.find_element_by_id("user_ip")
                print("已经登录了")
                return
            except Exception as e:
                print("connect 未知错误")
                n_time = datetime.now()
                print(n_time)
                printError(e)
        except Exception as e:
            print("connect main 错误")
            n_time = datetime.now()
            print(n_time)
            printError(e)


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
        print("isNetOK error")
        print(n_time)
        printError(e)
        return False

def network_check(connecter):
    isOK = isNetOK(('www.baidu.com',443))
    if not isOK:
        connecter.connect()
    else:
        return

if __name__ == "__main__":
    # 自动打卡
    reportor = Reportor(login_data['username'], login_data['password'])
    check_job(reportor, daily_report_data, temp_report_data)

    # 宿舍保持在线
    # connecter = Connecter(login_data['username'], login_data['password'])
    # network_check(connecter)

    # 自动打卡，自动任务
    scheduler_report = BlockingScheduler()
    scheduler_report.add_job(check_job, 'cron', day='*', hour=7, minute=11, args=[
        reportor, daily_report_data, temp_report_data
    ])

    # 宿舍保持在线，自动任务
    # scheduler_report.add_job(network_check, 'interval', minutes=5, args=[
    #     connecter
    # ])
    print("uestc_health \njob started")
    push("uestc_health \njob started")
    scheduler_report.start()
    push("我挂了")
    # if server_url is not None:
    #     requests.get(url=server_url+f'?text=我挂了 ')
