# ==================================必填项==================================

# webdriver_path为你的电脑上geckodriver的所在位置
webdriver_path = r"D:/geckodriver.exe"

# 首选项
preferences = {
    # 浏览器无痕，推荐 True
    "incognito_flag": True,

    # 浏览器无窗口，推荐 True
    "headless_flag": True,

    # 是否发送邮件，推荐 False 。若为 True ，需修改选填项的 push_email_server 和 push_email_list
    "email_flag": False,


    # 每日循环任务，推荐 False 。若为 True ，需修改必填项的 report_hour 和 report_min
    "report_flag": False,

    # 每日循环任务-小时
    # 【务必修改】避免大量人员同一时间打卡，0-23之间
    "report_hour": 9,

    # 每日循环任务-分钟
    # 0-59之间
    "report_min": 11,

    # 每日循环任务-自动平安打卡，推荐 False 
    # 若为 True 且 daily_report_flag_from_yesterday 为 False ，需修改选填项的 daily_report_login_data 和 daily_report_data
    "daily_report_flag": False,

    # 每日循环任务-自动平安打卡-使用昨日信息，推荐 True
    "daily_report_flag_from_yesterday": True,

    #【已停用，勿动】 每日循环任务-自动体温上报
    "temp_report_flag": False,


    # 校园无线网断网重连，推荐 False 。若为True，需修改选填项的 campusnet_login_data
    # 请勿在非校园无线网环境开启，否则会进入死循环
    "campusnet_flag": False,

    # 宿舍有线网断网重连，推荐 False 。若为True，需修改选填项的 dormnet_login_data
    # 请勿在非宿舍有线网环境开启，否则会进入死循环
    "dormnet_flag": False,
}

# ==================================选填项==================================
# 根据首选项选填下列信息
# 带注释的项都需要修改

# --------------------------------email_flag--------------------------------
# 推荐使用阿里云邮件推送服务

push_email_server = {
    # 推送域名
    "EMAIL_FROM": "",
    # 密码
    "EMAIL_HOST_PASSWORD": "",

    "EMAIL_HOST": "smtpdm.aliyun.com",
    "EMAIL_PORT": 80,
}

push_email_list = [{
    # 收件地址
    "mail": "",
    # 普通邮件标题
    "push": "UESTC health 服务器日常推送",
    # 异常邮件标题
    "error": "UESTC health 服务器异常",
},
    # {
    #     "mail":"",
    #     "title":"",
    # },
]

# ----------------------------daily_report_flag----------------------------
# 如果启用 daily_report_flag_from_yesterday，则不用填写以下信息

# 这里修改为你自己的信息，注释下的都需要修改
# 多人打卡逻辑为登陆一个账号，打一次卡，请注意顺序
# daily_report_data 和 daily_report_login_data 账户顺序需要一致

daily_report_login_data = [
    {
        # 学号
        "username": '',
        # 密码
        "password": '',
    },
    # {
    #     # 若要添加打卡人在此添加
    # },
]

daily_report_data = [{
    # 学号
    "USER_ID": "2020xxxx",
    # 姓名
    "USER_NAME": "xxx",
    # 学院
    "DEPT_NAME": "计算机科学与工程学院（网络空间安全学院）",
    # 性别
    "GENDER_CODE": "男",
    # 年龄
    "AGE": "21",
    # 电话
    "PHONE_NUMBER": "XXXXXX",
    # 身份证
    "IDCARD_NO": "xxxxxx",
    # 全日制学术硕士 || 电子信息
    "LB": "全日制学术硕士",
    # 学院代码
    "DEPT_CODE": "1008",
    # 导师
    "TUTOR": "xxxx",
    # 校区
    "LOCATION_DETAIL": "电子科技大学清水河校区",
    "WID": "",
    "CZR": "",
    "CZZXM": "",
    "PERSON_TYPE_DISPLAY": "留校",
    "PERSON_TYPE": "001",
    "LOCATION_PROVINCE_CODE_DISPLAY": "四川省",
    "LOCATION_PROVINCE_CODE": "510000",
    "LOCATION_CITY_CODE_DISPLAY": "成都市",
    "LOCATION_CITY_CODE": "510100",
    "LOCATION_COUNTY_CODE_DISPLAY": "郫都区",
    "LOCATION_COUNTY_CODE": "510117",
    "HEALTH_STATUS_CODE_DISPLAY": "正常",
    "HEALTH_STATUS_CODE": "001",
    "HEALTH_UNSUAL_CODE": "",
    "IS_HOT_DISPLAY": "否",
    "IS_HOT": "0",
    "IS_IN_HB_DISPLAY": "否",
    "IS_IN_HB": "0",
    "IS_HB_BACK_DISPLAY": "否",
    "IS_HB_BACK": "0",
    "IS_DEFINITE_DISPLAY": "否",
    "IS_DEFINITE": "0",
    "IS_QUARANTINE_DISPLAY": "否",
    "IS_QUARANTINE": "0",
    "IS_KEEP_DISPLAY": "否",
    "IS_KEEP": "0",
    "TEMPERATURE": "",
    "IS_SEE_DOCTOR_DISPLAY": "否",
    "IS_SEE_DOCTOR": "NO",
    "IS_IN_SCHOOL_DISPLAY": "是",
    "IS_IN_SCHOOL": "1",
    # 天府健康通，1表示“绿码”，其余情况不确定，猜测是2、3
    "TF_HEALTH_CODE": "1",
    # 疫苗接种情况，1表示“已全程接种”，其余情况不确定，猜测是2、3、4
    "VACCINATION": "1",
    "MEMBER_HEALTH_STATUS_CODE_DISPLAY": "正常",
    "MEMBER_HEALTH_STATUS_CODE": "001",
    "MEMBER_HEALTH_UNSUAL_CODE_DISPLAY": "",
    "MEMBER_HEALTH_UNSUAL_CODE": "",
    "REMARK": "",
    "SAW_DOCTOR_DESC": "",
},
    # {
    #     # 若要添加打卡人在此添加
    # },
]

# ----------------------------temp_report_flag----------------------------
# 【已停用】体温信息，不用填写
# 不能单独填报体温，需要同时平安打卡和填报体温

temp_report_data = []
for i in range(len(daily_report_data)):
    temp_report_data.append({"TEMPERATURE": "36"})
    temp_report_data[i]['USER_ID'] = daily_report_data[i]['USER_ID']
    temp_report_data[i]['USER_NAME'] = daily_report_data[i]['USER_NAME']
    temp_report_data[i]['DEPT_NAME'] = daily_report_data[i]['DEPT_NAME']
    temp_report_data[i]['DEPT_CODE'] = daily_report_data[i]['DEPT_CODE']
    temp_report_data[i]['WID'] = daily_report_data[i]['WID']

# -----------------------------dormnet_flag------------------------------
# 宿舍有线网登录账号

dormnet_login_data = [
    {
        # 学号
        "username": '',
        # 密码
        "password": '',
        # 服务商 China Mobile:中国移动 China Telecom:电信
        "service": '',
    },
    # {
    #     # 按目前逻辑，只需要登录一个人的账号就可以用网了
    # },
]

# ----------------------------campusnet_flag----------------------------
# 校园无线网登录账号

campusnet_login_data = [
    {
        # 学号
        "username": '',
        # 密码
        "password": '',
    },
    # {
    #     # 按目前逻辑，只需要登录一个人的账号就可以用网了
    # },
]
