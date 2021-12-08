from django.views.decorators.csrf import csrf_exempt
import requests

@csrf_exempt
def update_safe_zone():
    res = requests.get('http://3.37.163.203:8040/zone_manage/certify_1/')
    return


@csrf_exempt
def delete_expire_ttl():
    res = requests.get('http://3.37.163.203:8040/zone_manage/certify_2/')
    return