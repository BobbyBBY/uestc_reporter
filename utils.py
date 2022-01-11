import sys
import traceback
import push_server


def printError():
    exc_type, exc_value, exc_traceback = sys.exc_info()
    error_message = ""
    error_message += "str(exc_value):\n%s\n\n" % str(exc_value)
    error_message += "repr(exc_value):\n%s\n\n" % repr(exc_value)
    error_message += "e.type:\n%s\n\n" % str(exc_type)
    error_message += "e.traceback:\n%s\n\n" % str(exc_traceback)
    error_message += "traceback.format_exc():\n%s" % traceback.format_exc()
    print(error_message)
    push_server.push_error(error_message)


def cookies2str(cookies):
    cookie = [item["name"] + "=" + item["value"] for item in cookies]
    cookiestr = ";".join(item for item in cookie)
    return cookiestr
