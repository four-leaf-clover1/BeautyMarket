from django.contrib.auth.backends import ModelBackend
import re

from .models import User

def get_user_by_account(account):
    try:
        # 判断账号是用户名还是手机号
        if re.match(r'^1[3-9]\d{9}', account):
            # 如果是手机号就用mobile去查询
            user = User.objects.get(mobile=account)
        else:
            # 如果是用户名就用username去查询
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    else:
        return user



class UsernameMobileAuthBackend(ModelBackend):
    """自定义认证类。实现多账号登入"""

    def authenticate(self, request, username=None, password=None, **kwargs):

        user = get_user_by_account(username)
        #判断密码是否正确
        if user and user.check_password(password):
            #把user对象返回
            return user