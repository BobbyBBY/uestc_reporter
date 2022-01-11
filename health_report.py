from my_request import get_request
import json
import re
from datetime import datetime
import time
import slider

from push_server import push, push_error
from selenium import webdriver
from personal_info import (
    webdriver_path,
    daily_report_data,
    temp_report_data,
    daily_report_login_data,
    preferences,
)

import utils


class Reportor(object):
    def __init__(self):
        self.login_data = daily_report_login_data
        self.host = "eportal.uestc.edu.cn"
        self.login_url = "http://eportal.uestc.edu.cn/jkdkapp/sys/lwReportEpidemicStu/index.do?#/dailyReport"
        self.wid_url = "/jkdkapp/sys/lwReportEpidemicStu/modules/dailyReport/getMyTodayReportWid.do?"
        self.daily_report_check_url = "/jkdkapp/sys/lwReportEpidemicStu/modules/dailyReport/getMyDailyReportDatas.do?"
        self.daily_report_save_url = "/jkdkapp/sys/lwReportEpidemicStu/modules/dailyReport/T_REPORT_EPIDEMIC_CHECKIN_YJS_SAVE.do?"
        self.temp_report_check_url = "/jkdkapp/sys/lwReportEpidemicStu/mobile/tempReport/getMyTempReportDatas.do?"
        self.temp_report_save_url = "/jkdkapp/sys/lwReportEpidemicStu/mobile/tempReport/T_REPORT_TEMPERATURE_YJS_SAVE.do?"
        self.headless_flag = preferences["headless_flag"]  # 无窗口
        self.incognito_flag = preferences["incognito_flag"]  # 无痕
        self.email_flag = preferences["email_flag"]  # 邮件
        self.daily_report_flag = preferences["daily_report_flag"]  # 每日平安打卡
        self.temp_report_flag = preferences["temp_report_flag"]  # 每日体温上报
        self.headers = {"Cookie": ""}

    def get_explorer(self):
        options = webdriver.firefox.options.Options()
        if self.headless_flag:
            options.add_argument("--headless")  # 无窗口
        if self.incognito_flag:
            options.add_argument("--incognito")  # 无痕
        driver = webdriver.Firefox(executable_path=webdriver_path, options=options)
        return driver

    # 登录GMIS
    def login_GMIS(self, user):
        self.username = self.login_data[user]["username"]
        self.password = self.login_data[user]["password"]
        print("health_report logging in...\r", end="")
        driver = self.get_explorer()

        def _login_GMIS(i):
            print("第{}次尝试登录GMIS".format(i))
            # 输入账户、密码，点击登录按钮，激活滑块验证
            try:
                js = """
                    var casLoginForm = document.getElementById("casLoginForm");
                    var username = document.getElementById("username");
                    var password = document.getElementById("password");
                    username.value = "{}"
                    password.value = "{}"
                    _etd2(password.value, document.getElementById("pwdDefaultEncryptSalt").value);
                    login_button = $(".auth_login_btn").filter(".primary").filter(".full_width")
                    login_button.click()
                """.format(
                    self.username, self.password
                )
                driver.execute_script(js)
                time.sleep(3)

                # 获取滑块验证的两个图片
                bigImg_base64 = driver.find_element_by_id("img1").get_attribute("src")
                smallImg_base64 = driver.find_element_by_id("img2").get_attribute("src")
                # 计算滑块需要滑动的距离
                moveLengthScale = slider.findSliderX(bigImg_base64, smallImg_base64)
                # 应该动态获取幕布宽度，但其实写死了
                # canvasLength =
                canvasLength = 280
                moveLength = round(280 * moveLengthScale)
                # print("moveLength " +str(moveLength))
                # 向验证服务器发送答案，获得验证结果sign
                # casLoginForm加入sign后，提交表单
                js1 = """
                    var sign = ""
                    var verifySliderImageCode =function (canvasLength,moveLength) {
                        $.ajax({
                            url: "verifySliderImageCode.do",
                            dataType: 'json',
                            data: {
                                "canvasLength": canvasLength,
                                "moveLength": moveLength
                            },
                            success: function (data) {
                                console.log(data)
                                sign = data.sign
                                var casLoginForm = $("#casLoginForm");
                                var signInput=$("<input type='hidden' name='sign'/>");
                                signInput.attr("value", sign);
                                casLoginForm.append(signInput);
                                casLoginForm.submit();
                            }
                        })
                    };
                """
                js2 = """ 
                    verifySliderImageCode({},{})
                """.format(
                    canvasLength, moveLength
                )
                js = js1 + js2
                driver.execute_script(js)
                time.sleep(3)
            except Exception as e:
                # printError(e)
                # 平均需要验证2次，如果验证失败，返回的data里没有sign
                pass

        # 检测登录状态
        def _check_login_GMIS():
            try:
                driver.find_element_by_xpath(
                    "/html/body/header/header[1]/div/div/div[4]/div[1]/img"
                ).click()
                time.sleep(2)
                username = driver.find_element_by_xpath(
                    "/html/body/div[5]/div[2]/div[1]"
                ).text
            except Exception:
                # 登录失败，5秒后退出
                time.sleep(5)
                return False
            else:
                # 登录成功,记录cookies就退出了
                print("GMIS登录账号 : {}".format(username))
                Cookies = driver.get_cookies()
                driver.quit()
                self.headers["Cookie"] = utils.cookies2str(Cookies)
                return True

        # 尝试登录十次
        for i in range(10):
            driver.get(self.login_url)
            time.sleep(3)
            if _check_login_GMIS():
                return
            _login_GMIS(i + 1)
            if _check_login_GMIS():
                return
        if self.email_flag:
            push_error("GMIS登录失败，上服务器看看我觉得我还有救")
        raise RuntimeError("GMIS登录失败")

    # 每日平安打卡
    def daily_report(self, NEED_DATE, daily_report_data):
        def _daily_report(NEED_DATE, daily_report_data):
            # 获取WID
            wid_data = {
                "pageNumber": "1",
                "pageSize": "10",
                "USER_ID": daily_report_data["USER_ID"],
            }
            res = get_request(self.host, "POST", self.wid_url, wid_data, self.headers)
            if re.search("<title>统一身份认证</title>", res):
                raise RuntimeError("Cookie失效")
            elif re.search("<title>302 Found</title>", res):
                raise RuntimeError("Cookie失效")
            try:
                wid_json_loads = json.loads(res)
                wid = wid_json_loads["datas"]["getMyTodayReportWid"]["rows"][0]["WID"]
                daily_report_data["WID"] = wid
            except json.decoder.JSONDecodeError:
                print("json解析失败")
                return 1

            # check
            check_data = {
                "pageNumber": "1",
                "pageSize": "10",
                "USER_ID": daily_report_data["USER_ID"],
                "KSRQ": NEED_DATE,
                "JSRQ": NEED_DATE,
            }
            res = get_request(
                self.host, "POST", self.daily_report_check_url, check_data, self.headers
            )
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
                if parsed_res["datas"]["getMyDailyReportDatas"]["totalSize"] > 0:
                    print("daily report has finished")
                    return 0  # 打卡成功
            except KeyError:
                pass

            # save
            daily_report_data.update(
                {"NEED_CHECKIN_DATE": NEED_DATE, "CZRQ": NEED_DATE + " 00:00:00",}
            )
            res = get_request(
                self.host,
                "POST",
                self.daily_report_save_url,
                daily_report_data,
                self.headers,
            )
            if re.search("<title>统一身份认证</title>", res):
                raise RuntimeError("Cookie失效")
            elif re.search("<title>302 Found</title>", res):
                raise RuntimeError("Cookie失效")
            try:
                parsed_res = json.loads(res)
            except json.decoder.JSONDecodeError:
                print("json解析失败")
                return 1
            if (
                parsed_res["code"] == "0"
                and parsed_res["datas"]["T_REPORT_EPIDEMIC_CHECKIN_YJS_SAVE"] == 1
            ):
                print("daily report sucessful")
                return 0  # 打卡成功
            else:
                print("打卡失败")
                return 1

        try:
            return _daily_report(NEED_DATE, daily_report_data)
        except RuntimeError as e:
            if self.email_flag:
                push_error(str(e) + "，上服务器看看我觉得我还有救")
            exit(0)
        except Exception:
            return 1

    # 每日体温上报
    def temp_report(self, NEED_DATE, DAY_TIME, temp_report_data):
        def _temp_report(NEED_DATE, DAY_TIME, temp_report_data):
            check_data = {
                "USER_ID": temp_report_data["USER_ID"],
                "NEED_DATE": NEED_DATE,
                "DAY_TIME": DAY_TIME,
            }
            res = get_request(
                self.host, "POST", self.temp_report_check_url, check_data, self.headers
            )
            if re.search("<title>统一身份认证</title>", res):
                raise RuntimeError("Cookie失效")
            elif re.search("<title>302 Found</title>", res):
                raise RuntimeError("Cookie失效")
            if (
                re.search(
                    '"NEED_DATE":"{}","DAY_TIME":"{}"'.format(NEED_DATE, DAY_TIME), res
                )
                is not None
            ):
                print("temp report {} has finished".format(DAY_TIME))
                return int(DAY_TIME)

            # save
            DAY_TIME_DISPLAY = {
                "1": "早上",
                "2": "中午",
                "3": "晚上",
            }
            temp_report_data.update(
                {
                    "DAY_TIME": DAY_TIME,
                    "DAY_TIME_DISPLAY": DAY_TIME_DISPLAY[DAY_TIME],
                    "NEED_DATE": NEED_DATE,
                }
            )

            res = get_request(
                self.host,
                "POST",
                self.temp_report_save_url,
                temp_report_data,
                self.headers,
            )
            if re.search("<title>统一身份认证</title>", res):
                raise RuntimeError("Cookie失效")
            elif re.search("<title>302 Found</title>", res):
                raise RuntimeError("Cookie失效")
            try:
                assert (
                    re.search(r'"T_REPORT_TEMPERATURE_YJS_SAVE":(?P<r_value>\d)', res)[
                        "r_value"
                    ]
                    == "1"
                )
                print("temp report {} sucessful".format(DAY_TIME))
                return int(DAY_TIME)  # 打卡成功
            except Exception:
                time.sleep(5)
                return 0

        try:
            return _temp_report(NEED_DATE, DAY_TIME, temp_report_data)
        except RuntimeError as e:
            if self.email_flag:
                push_error(str(e) + "，上服务器看看我觉得我还有救")
            exit(0)
        except Exception:
            return 1

    # 打卡自动化
    def daily_check(self):
        def _daily_check(user, daily_report_data, temp_report_data, date_str=None):
            # 登录
            self.login_GMIS(user)

            if date_str is None:
                date_str = datetime.now().strftime("%Y-%m-%d")
                print("当前时间 : " + str(datetime.now()))
            # 平安打卡
            if self.daily_report_flag:
                while self.daily_report(date_str, daily_report_data):
                    continue
            # 每日体温上报
            if self.temp_report_flag:
                r_value_list = []
                for id in range(1, 4):
                    while id not in r_value_list:
                        r_value_list.append(
                            self.temp_report(date_str, str(id), temp_report_data)
                        )
            # 打卡全部完成
            print(
                "{} day {} report complete!\n".format(
                    daily_report_data["USER_NAME"], date_str
                )
            )
            return date_str

        date_str = "blank"
        for user in range(len(daily_report_data)):
            date_str = _daily_check(
                user, daily_report_data[user], temp_report_data[user]
            )
        if self.email_flag:
            push(date_str + " 打卡完成")


# # 自动打卡
# reportor = Reportor()
# reportor.daily_check()
