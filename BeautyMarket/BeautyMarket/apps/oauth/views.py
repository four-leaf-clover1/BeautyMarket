from django.shortcuts import render,redirect
from QQLoginTool.QQtool import OAuthQQ
from django.views import View
from django.conf import settings
from django import http
from BeautyMarket.utils.response_code import RETCODE
import logging
from django.contrib.auth import login


from .models import OAuthQQUser
# Create your views here.


logger = logging.getLogger('django')


class OAuthURLView(View):

    def get(self,request):

        next = request.GET.get("next","/")

        oauth = OAuthQQ(
            client_id=settings.QQ_CLIENT_ID,
            client_secret=settings.QQ_CLIENT_SECRET,
            redirect_uri=settings.QQ_REDIRECT_URI,
            state=next

        )

        #调用SDK中  get_qq_url方法得到拼接好的qq登入的url
        login_url = oauth.get_qq_url()

        #响应
        return http.JsonResponse({"code": RETCODE.OK,"errmsg": "OK","login_url": login_url})


class QQAuthUserView(View):

    def get(self,request):

        #获取查询参数中的code
        code = request.GET.get('code')

        #判断code是否获取到了
        if code is None:
            return http.HttpResponseForbidden("缺少参数")

        #创建OAuthQQ 对象
        oauth = OAuthQQ(
            client_id=settings.QQ_CLIENT_ID,
            client_secret=settings.QQ_CLIENT_SECRET,
            redirect_uri=settings.QQ_REDIRECT_URI,


        )
        try:
            #通过code 获取access_token
            access_token = oauth.get_access_token(code)

            #通过access_token获取openid
            openid = oauth.get_open_id(access_token)
        except Exception as er:
            logger.error(er)
            return http.HttpResponseServerError("QQ登入失败")

        try:
            oauth_model = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            #如果查询不到说明为绑定过用户，使其与美多商城进行绑定
            context = {
                'openid' : openid

            }

            return render(request,"oauth_callback.html",context)

        else:
            #如果查询到了openid说明已经绑定过了，直接登入即可
            user = oauth_model.user
            login(request,user)
            response = redirect(request.GET.get('state') or '/')
            response.set_cookie('username',user.username,max_age=settings.SESSION_COOKIE_AGE)
            return response











