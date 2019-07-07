from django.shortcuts import render
from django.views import View

# Create your views here.

class IndexView(View):
    """设置首页"""

    def get(self,request):

        return render(request,"index.html")

