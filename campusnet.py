from datetime import datetime
import time
import socket
import threading

from push_server import push, push_error
from selenium import webdriver
from personal_info import campusnet_login_data, webdriver_path, preferences


class Reportor(object):
    def __init__(self):
        self.login_data = campusnet_login_data
        self.login_url = "http://10.253.0.213/srun_portal_success?ac_id=1&theme=pro"
        self.headless_flag = preferences["headless_flag"]  # 无窗口
        self.incognito_flag = preferences["incognito_flag"]  # 无痕
        self.email_flag = preferences["email_flag"]  # 邮件

    def get_explorer(self):
        options = webdriver.firefox.options.Options()
        if self.headless_flag:
            options.add_argument("--headless")  # 无窗口
        if self.incognito_flag:
            options.add_argument("--incognito")  # 无痕
        driver = webdriver.Firefox(executable_path=webdriver_path, options=options)
        return driver

    # 登录校园无线网
    def login_campusnet(self):
        user = 0
        self.username = self.login_data[user]["username"]
        self.password = self.login_data[user]["password"]
        print("campusnet logging in...\r", end="")
        driver = self.get_explorer()

        def _login_campusnet(i):
            print("校园网第{}次尝试登录".format(i))
            try:
                js = """
                    var username = document.getElementById("username");
                    var password = document.getElementById("password");
                    username.value = "{}"
                    password.value = "{}"
                    login_button = document.getElementById("login-account");
                    login_button.click()
                """.format(
                    self.username, self.password
                )
                driver.execute_script(js)
                time.sleep(3)

            except Exception as e:
                # 平均需要验证2次
                pass

        # 检测登录状态
        def _check_login_campusnet():
            try:
                # driver.find_element_by_id("logout").click()
                driver.find_element_by_id("logout")
            except Exception:
                # 登录失败，5秒后退出
                n_time = datetime.now()
                print(str(n_time) + " 校园网尝试登录失败")
                time.sleep(5)
                return False
            else:
                print("校园网登录账号 : {}".format(self.username))
                n_time = datetime.now()
                if self.email_flag:
                    push(str(n_time) + " 校园网连上了 ^_^")
                driver.quit()
                return True

        # 尝试登录十次
        for i in range(10):
            driver.get(self.login_url)
            time.sleep(3)
            if _check_login_campusnet():
                return
            _login_campusnet(i + 1)
            if _check_login_campusnet():
                return
        if self.email_flag:
            push_error("校园网登录失败，上服务器看看我觉得我还有救")
        raise RuntimeError("校园网登录失败")

    def isNetOK(self, testserver):
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
            print(str(n_time) + " campusnet offline")
            if self.email_flag:
                push_error(str(n_time) + " 校园网断了。。。")
            return False

    def network_check(self):
        netIsOK = self.isNetOK(("www.baidu.com", 443))
        if netIsOK:
            return
        else:
            self.login_campusnet()

    # 断网自动登录
    def auto_login_campusnet(self):
        def _auto_login_campusnet():
            n_time = datetime.now()
            print(str(n_time) + " 校园无线网守护已开启")
            while True:
                self.network_check()
                time.sleep(60 * 5)  # 10分钟检查一次网络
                """
                # test
                time.sleep(15)
                n_time = datetime.now()
                print(str(n_time) + " test")
                """

        self.network_check()
        thread = threading.Thread(target=_auto_login_campusnet)
        thread.setDaemon(True)
        thread.start()


# # 校园无线网断网重连
# reportor = Reportor()
# reportor.auto_login_campusnet()
# input()
