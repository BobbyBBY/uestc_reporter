from push_server import push
from personal_info import preferences
from apscheduler.schedulers.blocking import BlockingScheduler
import campusnet
import dormnet
import health_report
import utils


if __name__ == "__main__":
    try:
        report_flag = preferences["report_flag"]
        campusnet_flag = preferences["campusnet_flag"]
        dormnet_flag = preferences["dormnet_flag"]

        # 校园无线网断网重连
        if campusnet_flag:
            campusnet_reportor = campusnet.Reportor()
            campusnet_reportor.auto_login_campusnet()

        # 宿舍有线网断网重连
        if dormnet_flag:
            dormnet_reportor = dormnet.Reportor()
            dormnet_reportor.auto_login_dormnet()

        # 自动打卡
        if report_flag:
            health_reportor = health_report.Reportor()
            health_reportor.daily_check()

            # 自动打卡，自动任务
            scheduler_health_report = BlockingScheduler()
            scheduler_health_report.add_job(
                health_reportor.daily_check, "cron", day="*", hour=preferences["report_hour"], minute=preferences["report_min"],
            )
            print("uestc_health \njob started")
            push("uestc_health \njob started")
            scheduler_health_report.start()

        input()
    except:
        utils.printError()
