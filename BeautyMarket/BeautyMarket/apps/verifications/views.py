from django.shortcuts import render
from django.views import View
from BeautyMarket.libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from django import http
from BeautyMarket.utils.response_code import RETCODE
from random import randint
from BeautyMarket.libs.yuntongxun.sms import CCP
import logging

logger = logging.getLogger('django')
# Create your views here.

class ImageCodeView(View):
    """图形验证码"""
    def get(self,request,uuid):
        name,text, image_bytes = captcha.generate_captcha()

        # 创建redis连接对象
        redis_conn = get_redis_connection("verify_code")
        redis_conn.setex(uuid,300,text)

        return http.HttpResponse(image_bytes,content_type="image/png")


class SMSCodeView(View):
    """发送短信验证码"""
    # this.host + '/sms_codes/' + this.mobile + '/?image_code=' + this.image_code + '&uuid=' + this.uuid;

    def get(self,request,mobile):
        # 接收前端数据
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('uuid')


        # 校验
        if all([image_code_client,uuid]) is False:
            return http.HttpResponseForbidden('缺少必要参数')

        # 创建redis连接对象
        redis_conn = get_redis_connection("verify_code")

        # 获取redis中图形验证码
        image_code_server = redis_conn.get(uuid)
        # 直接将redis中用过的图形验证码删除(让每个图形验证码都是一次性的）
        redis_conn.delete(uuid)

        # 判断图形验证码有没有过期
        if image_code_server is None:
            return http.JsonResponse({"code":RETCODE.IMAGECODEERR,"errmsg":"图形验证码已过期"})

        # 判断用户输入的验证码与redis中之前存储的验证码是否一致
        if image_code_client.lower() != image_code_server.decode().lower():
            return http.JsonResponse({"code":RETCODE.IMAGECODEERR,"errmsg":"图形验证码输入错误"})


        # 随机生成一个6位数字来当短信验证码
        sms_code = "%06d" % randint(0,999999)
        logger.info(sms_code)
        # 把短信验证码存储到redis中以备后期注册时校验
        redis_conn.setex("sms_code_%s" % mobile,300,sms_code)

        # 利用第三方容联云发短信
        CCP().send_template_sms(mobile,[sms_code,5],1)

        # 响应
        return http.JsonResponse({"code":RETCODE.OK,"errmsg":"OK"})





