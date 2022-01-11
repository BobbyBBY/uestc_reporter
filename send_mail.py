# -*- coding:utf-8 -*-
import smtplib
import email
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from personal_info import push_email_server


def SendMail(to_email, title, content):
    EMAIL_FROM = push_email_server["EMAIL_FROM"]  # 刚才配置的发信地址
    EMAIL_HOST_PASSWORD = push_email_server["EMAIL_HOST_PASSWORD"]  # 密码
    EMAIL_HOST = push_email_server["EMAIL_HOST"]
    EMAIL_PORT = push_email_server["EMAIL_PORT"]
    # 自定义的回复地址
    replyto = EMAIL_FROM
    msg = MIMEMultipart("alternative")
    msg["Subject"] = title
    msg["From"] = "%s <%s>" % ("admin", EMAIL_FROM)
    msg["To"] = "%s <%s>" % ("client", to_email)

    msg["Reply-to"] = replyto
    msg["Message-id"] = email.utils.make_msgid()
    msg["Date"] = email.utils.formatdate()
    textplain = MIMEText("{}".format(content), _subtype="plain", _charset="UTF-8")
    msg.attach(textplain)

    try:
        client = smtplib.SMTP()
        client.connect(EMAIL_HOST, EMAIL_PORT)
        # 开启DEBUG模式
        client.set_debuglevel(0)
        client.login(EMAIL_FROM, EMAIL_HOST_PASSWORD)
        client.sendmail(EMAIL_FROM, [to_email], msg.as_string())
        client.quit()
        return True
    except smtplib.SMTPConnectError as e:
        error_msg = "邮件发送失败，连接失败"
    except smtplib.SMTPAuthenticationError as e:
        error_msg = "邮件发送失败，认证错误:"
    except smtplib.SMTPSenderRefused as e:
        error_msg = "邮件发送失败，发件人被拒绝:"
    except smtplib.SMTPRecipientsRefused as e:
        error_msg = "邮件发送失败，收件人被拒绝:"
    except smtplib.SMTPDataError as e:
        error_msg = "邮件发送失败，数据接收拒绝:"
    except smtplib.SMTPException as e:
        print(e)
    except Exception as e:
        error_msg = "邮件发送异常, {}".format(str(e))
    print(error_msg)
    return False
