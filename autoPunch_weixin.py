#coding: utf-8
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger

import datetime
import os,sys
import time
import requests
import logging, pytz,random

import datetime

# 判断 2018年4月30号 是不是节假日
from chinese_calendar import  is_holiday


# BlockingSchedulery
ISOTIMEFORMAT = '%m-%d %H:%M:%S'
JOB_DATE = "%Y-%m-%d %H:%M:%S"
TOPICID = '149' #149.test   148 pro
timezone = pytz.timezone("Asia/Shanghai")

job_defaults = {
    "coalesce": True,  # 默认为新任务关闭合并模式
    "max_instances": 1,  # 设置新任务的最大实例数为2
}

scheduler = BlockingScheduler(job_defaults=job_defaults,timezone=timezone)

logging.basicConfig(filename='D:\\workProject\\pthon\\autoPunch\\LOG\\log.log',format='[%(asctime)s-%(filename)s-%(levelname)s:%(message)s]', level = logging.DEBUG,filemode="a",datefmt='%Y-%m-%d%I:%M:%S %p')

def triggerMorning(job_date):
    triggerMorning = DateTrigger( run_date=datetime.datetime(job_date.year, job_date.month, job_date.day, 8, random.randint(0, 20), random.randint(0, 59)))
    scheduler.add_job(click, triggerMorning,args=['morning'], id='triggerMorning',replace_existing=True)

    # triggerAfternoon = DateTrigger( run_date=datetime.datetime(job_date.year, job_date.month, job_date.day, 17, random.randint(31, 59),random.randint(0, 59)))
    # scheduler.add_job(click, triggerAfternoon, args=['afternoon'], id='triggerAfternoon',replace_existing=True)


def triggerAfternoon(job_date):
    triggerAfternoon = DateTrigger(run_date=datetime.datetime(job_date.year, job_date.month, job_date.day, 17, random.randint(31, 59),random.randint(0, 59)))
    scheduler.add_job(click, triggerAfternoon,args=['afternoon'], id='triggerAfternoon',replace_existing=True)


# 输出时间
def job():
    logging.info("-------程序已正常启动，请等待自动打卡-------")
    print("-------程序已正常启动，请等待自动打卡-------")
    pro()
    scheduler.start()

def test():#测试
    # from apscheduler.triggers.interval import IntervalTrigger
    # intervalTrigger = IntervalTrigger(seconds=80,jitter=1)
    # scheduler.add_job(click, intervalTrigger,id="3",timezone=timezone,replace_existing=True)
    # triggerMorning = CronTrigger(day_of_week='mon-fri', hour=19, minute=46, second=35)
    #triggerAfternoon = CronTrigger(day_of_week='mon-fri', hour=17, minute=55)
    # scheduler.add_job(test2, triggerMorning, id="triggerMorning", replace_existing=True,args=[1])
    # scheduler.add_job(click, triggerAfternoon, id="triggerAfternoon", replace_existing=True)
    # a =  scheduler.remove_job("triggerMorning")
    # print("=====",a)
    # scheduler.add_job(click, triggerMorning, id="triggerMorning", replace_existing=True)
    # scheduler.reschedule_job('triggerMorning', trigger='cron', minute='35')
    # triggerMorning = CronTrigger(day_of_week='mon-fri', hour=8, minute=0, second=random.randint(0, 59))
    # triggerAfternoon = CronTrigger(day_of_week='mon-fri', hour=0, minute=4, second=random.randint(0, 59))
    # scheduler.add_job(click, triggerMorning, id="triggerMorning", replace_existing=True, args=[1])
    # scheduler.add_job(click, triggerAfternoon, id="triggerAfternoon", replace_existing=True, args=[2])
    print("---test--")

def pro():#正式环境
    global TOPICID
    TOPICID = '148'
    job_date = datetime.datetime.now()
    triggerMorning = CronTrigger(day_of_week='mon-fri', hour=8, minute=0, second=random.randint(0, 59))
    triggerAfternoon = CronTrigger(day_of_week='mon-fri', hour=17, minute=35, second=random.randint(0, 59))
    scheduler.add_job(click, triggerMorning, id="oneMorning", replace_existing=True, args=['oneMorning'])
    scheduler.add_job(click, triggerAfternoon, id="oneAfternoon", replace_existing=True, args=['oneAfternoon'])
    # triggerAfternoon = DateTrigger(run_date=datetime.datetime(job_date.year, job_date.month, 3, 8,random.randint(0, 10),random.randint(0, 59)))
    # scheduler.add_job(click, triggerAfternoon,args=['afternoon'] ,id='trigger',replace_existing=True)

def ResetPunch(args):#重设打卡
    newDate = datetime.datetime.now() + datetime.timedelta(days=1)
    while is_holiday(newDate):
        newDate = newDate + datetime.timedelta(days=1)
    if 'morning' == args:
        triggerMorning(newDate)
    elif 'afternoon' == args:
        triggerAfternoon(newDate)
    elif 'oneMorning' == args:
        scheduler.remove_job("oneMorning")
        triggerMorning(newDate)
    elif 'oneAfternoon' == args:
        scheduler.remove_job("oneAfternoon")
        triggerAfternoon(newDate)
    else:
        logging.warn("重设打卡异常")

    logging.debug(scheduler.get_jobs())
    logging.debug(scheduler.print_jobs())

def click(args):
    #打第一个卡
    print("-------打卡运行中-------")
    returnFlag =os.system('adb shell input keyevent 26')  # 点亮屏幕
    time.sleep(5)
    if(returnFlag != 0):#重新连接客户端
        print("returnFlag=", returnFlag)
        returnConnect= os.system('adb connect 192.168.20.102')
        if(returnConnect != 0):
            time.sleep(30)
            returnConnect = os.system('adb connect 192.168.20.102')
        print("connect=",returnConnect )
        time.sleep(20)
    returnFlag = os.system('adb shell input keyevent 82')  # 点亮屏幕
    print("returnFlag22=", returnFlag)
    time.sleep(3)
    if (returnFlag != 0):
        wxpusher('请注意,打卡异常')
        sys.exit(0)
    ResetPunch(args) #重设打卡
    os.system('adb shell input keyevent 82')  # 点亮屏幕
    time.sleep(1)
    os.system('adb shell am force-stop com.tencent.wework')  # 关闭微信
    time.sleep(1)
    os.system('adb shell input swipe 300 1000 300 500')  # 往上滑动
    time.sleep(1)
    os.system('adb shell input keyevent 3')  # 单击home键，回到主页
    time.sleep(1)
    os.system('adb shell input tap 1620 800')  # 点击企业微信
    time.sleep(5)
    os.system('adb shell input tap 678 1820')
    time.sleep(5)
    os.system('adb shell input tap 410 430')
    time.sleep(10)
    # os.system('adb shell input tap 540 1340')
    # time.sleep(5)
    os.system("adb shell input keyevent 4 ")# 返回
    time.sleep(1)
    os.system("adb shell am force-stop com.tencent.wework")  # 返回
    time.sleep(1)
    print("-------打卡完成-------")
    wxpusher("打卡成功")

def wxpusher(information):
    #推送消息给微信，此处可以删除，仅为通知 AT_4HSc6sCPTFGitUoEkfe4gmntD3gvw19e
    theTime = datetime.datetime.now().strftime(ISOTIMEFORMAT)
    url = 'http://wxpusher.zjiecode.com/api/send/message/?appToken=AT_4HSc6sCPTFGitUoEkfe4gmntD3gvw19e&content='+theTime+' '+information+'&topicId='+TOPICID;
    headers = {'Connection': 'close'}
    try:
        time.sleep(10)
        requests.get(url, headers=headers)
    except Exception as inst:
        logging.info(inst)
        logging.warning(inst)
        print("Exception")
        time.sleep(10)
        requests.get(url, headers=headers)
    finally:
        print("-------"+information+",等待下一次打卡-------")
        #sys.exit(0)

def main():
    job()



if __name__ == '__main__':
    main()