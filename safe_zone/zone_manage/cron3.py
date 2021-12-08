from django.views.decorators.csrf import csrf_exempt
import requests

@csrf_exempt
def check():
    for i in range(20):
        res = requests.get('http://3.37.163.203:8010/zone_manage/certify_predict/'+ str(i) + '/')
    return