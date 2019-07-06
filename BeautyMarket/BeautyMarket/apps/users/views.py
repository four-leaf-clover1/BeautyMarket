from django.shortcuts import render
from django.views import View
from django import http
import re
from .models import User
from django.contrib.auth import login
from BeautyMarket.utils.response_code import RETCODE
from django_redis import get_redis_connection
# Create your views here.

class RegisterView(View):
    '''注册'''

    def get(self,request):
        """ 提供注册页面"""
        return render(request,"register.html")

    def post(self,request):
        """注册逻辑"""
        # 接受请求表单数据
        query_dict = request.POST

        username = query_dict.get("username")
        password = query_dict.get("password")
        password2 = query_dict.get("password2")
        mobile = query_dict.get("mobile")
        sms_code_client = query_dict.get("sms_code")
        allow = query_dict.get("allow")

        # 校验
        # if all(query_dict.dict().values()) is False:
        if all([username, password, password2, mobile, sms_code_client, allow]) is False:

            return http.HttpResponseForbidden("缺少必要参数")
        if not re.match(r"^[a-zA-Z0-9_-]{5,20}$",username):

            return http.HttpResponseForbidden("请输入5-20个字符的用户名")
        if not re.match(r"^[0-9A-Za-z]{8,20}$", password):

            return http.HttpResponseForbidden("请输入8-20个字符的用户名")
        if password != password2:

            return http.HttpResponseForbidden("两次密码输入的不一致")
        if not re.match(r"^1[3-9]\d{9}$",mobile):

            return http.HttpResponseForbidden("请输入正确的手机号码")
        #
        # 创建redis连接对象
        redis_conn = get_redis_connection("verify_code")
        # 获取短信验证码
        sms_code_server = redis_conn.get("sms_code_%s" % mobile)
        # 让短信验证码只能用一次
        redis_conn.delete("sms_code_%s" % mobile)
        # 判断是否过期
        if sms_code_server is None:
            return http.HttpResponseForbidden("短信验证码过期")
        # 判断短信验证码是否正确
        if sms_code_client != sms_code_server.decode():
            return http.HttpResponseForbidden("短信验证码输入错误")

        # 创建一个新用户
        user=User.objects.create_user(username=username,password=password,mobile=mobile)
        login(request,user)

        return http.HttpResponse("注册成功，跳转到首页")



class UsernameCountView(View):
    """判断用户名是否重复"""
    def get(self,request,username):
        # 以username查询user模型,再取它的count, 0:代表用户名没有重复, 1代表用户名重复
        count = User.objects.filter(username=username).count()
        return http.JsonResponse({'code':RETCODE.OK,'errmsg': 'OK', 'count': count})


class MobileCountView(View):
    """判断手机号是否重复"""
    def get(self,request,mobile):
        # 以username查询user模型,再取它的count, 0:代表用户名没有重复, 1代表用户名重复
        count = User.objects.filter(mobile=mobile).count()
        return http.JsonResponse({'code':RETCODE.OK,'errmsg': 'OK', 'count': count})






