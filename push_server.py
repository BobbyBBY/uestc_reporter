from send_mail import SendMail
from personal_info import push_email_list

def push(content):
    for i in range(len(push_email_list)):
        SendMail(push_email_list[i]["mail"],push_email_list[i]["push"],content)

def push_error(content):
    for i in range(len(push_email_list)):
        SendMail(push_email_list[i]["mail"],push_email_list[i]["error"],content)