from celery_tasks.sms.yuntongxun.sms import CCP
from celery_tasks.sms import constants
from celery_tasks.main import celery_app


@celery_app.task() #把下面函数装饰为一个celery任务
def send_sms_code(mobile,sms_code):
    #利用第三方容联云发短信
    CCP().send_template_sms(mobile,[sms_code,constants.SMS_CODE_EXPIRE_REDIS // 60],1)