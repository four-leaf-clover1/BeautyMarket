from django.shortcuts import render, redirect
from django.views import View
from django import http
import re
from .models import User
from django.contrib.auth import login, authenticate,logout,mixins
from BeautyMarket.utils.response_code import RETCODE
from django_redis import get_redis_connection
from django.conf import settings
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

        return redirect('/login/')



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


class LoginView(View):
    """登入界面"""
    def get(self,request):
        return render(request,"login.html")

    #接收表单数据
    def post(self,request):
        query_dict = request.POST
        username = query_dict.get("username")
        password = query_dict.get("password")
        remembered = query_dict.get("remembered")

        # if re.match(r'1[3-9]\d{9}$',username):
        #     User.USERNAME_FIELD = 'mobile'

    #校验,用户认证
        user = authenticate(request,username=username,password=password)
        # User.USERNAME_FIELD = "username"
        if user is None:
            return render(request,"login.html",{'account_errmsg':"用户名密码错误"})
    #状态保持
        login(request,user)
        # 如果用户没有记住登入
        if remembered != 'on':
            request.session.set_expiry(0)
        # request.session.set_expiry((60*60*48) if remembered else 0)

        # return http.HttpResponse("登入成功，来到首页")
        #/login/?next=/info/
        #/login/
        response =  redirect(request.GET.get('next') or '/')
        # response.set_cookie('username',user.username,max_age=settings.SESSION_COOKIE_AGE if remembered else 0)
        response.set_cookie('username', user.username, max_age=settings.SESSION_COOKIE_AGE if remembered else None)

        return response


class LogoutView(View):
    """退出登入"""

    def get(self,request):

        #消除状态保持
        logout(request)
        # 重定向到登入界面
        response = redirect('/login/')

        #删除cookie中的username
        response.delete_cookie('username')

        return response


class InfoView(mixins.LoginRequiredMixin,View):
    """用户中心"""
    # def get(self,request):
    #     # if isinstance(request.user,User):
    #     if request.user.is_authenticated:
    #
    #         return render(request,"user_center_info.html")
    #     else:
    #         return redirect('/login/?next=/info/')

    def get(self,request):
        return render(request,"user_center_info.html")




