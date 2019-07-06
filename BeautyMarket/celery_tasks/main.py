from celery import Celery

# 创建celery实例对象
celery_app = Celery("meiduo")


# 加载配置（指定中间人）
celery_app.config_from_object("celery_tasks.config")


# 指定celery可以生成的任务
celery_app.autodiscover_tasks(["celery_tasks.sms"])