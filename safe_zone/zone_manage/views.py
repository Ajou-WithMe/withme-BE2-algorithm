# Create your views here.
import copy

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.csrf import csrf_exempt
from .models import SafeZone, User, ZoneLocation,UserOption,Location, InitSafeZone
from .serializers import InitSafeZoneSer
from rest_framework.parsers import JSONParser
from . import connectDB, constants, vertify, util
import json, jwt, base64, struct
from django.utils import timezone
from datetime import datetime, timedelta
import pytz


'''
if request.method == 'GET':
        connectDB.uuuser()
        #serializer = AddressesSerializer(query_set, many=True) 이렇게 query 결과를 serializer에 담아주기만 하면 json으로 뽑아줌!!!
        return HttpResponse('GET' + ' jongseong') #JsonResponse(serializer.data, safe=False)
elif request.method == 'POST':
        data = JSONParser().parse(request)
        print(data)
        data1 = {
            "success": 200,
            "status": 401,
            "data": data
        }
        received_json_data = json.loads(request.body)
        return JsonResponse(data1, safe=False) #content_type='applictaion/json'
'''
@csrf_exempt
def connect(request):
    connectDB.con_nect()
    data1 = {
        "success": 201,
        "status": True,
    }
    return JsonResponse(data1, safe=False)


@csrf_exempt
def Init_SafeZone(request):
    return_status = 204;success = False
    if request.method == 'POST':
        auth_token = request.headers.get("AccessToken", None)
        if auth_token == None:# 토큰 값이 아예 안 들어왔을 때 401 코드 처리 및 메시지 출력
            return JsonResponse({'message': 'Enter the token.'}, status=401)
        '''
        padded = auth_token + "=" * divmod(len(auth_token), 4)[1]
        jsondata = base64.urlsafe_b64decode(padded)#현재 받은 토큰은, 손상된(변경된) 토큰임을 꼭 기억하기
        jsonbyte = bytearray(jsondata)
        cache_i1=0;cache_i2=0;count=0
        for i in range(len(jsonbyte)):
            if jsonbyte[i] == 34:                count+=1
            if count == 6:cache_i1=i
            if count == 8: cache_i2=i;break
        constants.new_uid = jsonbyte[cache_i1+2:cache_i2].decode('utf-8')
        '''
        # 받은 토큰 디코딩해서 user id 정보 출력하기
        jwt_options = {
            'verify_signature': False,
            'verify_exp': True,
            'verify_sub': True,
            'verify_nbf': False,
            'verify_iat': False,  # True,
            'verify_aud': False
        }
        try:
            jsondata = jwt.decode(auth_token, 'dkwndnlemal123!', algorithms=['HS256'], options=jwt_options)
        except:
            return JsonResponse({'message': 'token expired.'}, status=401)
        #constants.new_uid =str(jsondata['sub'])
        data = JSONParser().parse(request)

        #constants.old_vertex, constants.new_uid =[tuple(data['safeZone'][k].values()) for k in range(len(data['safeZone']))], uid #str(uid)
        constants.old_vertex = [tuple(data['safeZone'][k].values()) for k in range(len(data['safeZone']))]
        stat, total_max_x, total_min_y = vertify.zone_min_size(constants.old_vertex) #여기까지가 20ms

        if stat == 1:  # 여기는 임시 변수만 사용하기.(새로운 유저들이 각자꺼만 저장해야하므로)
            #1101#geodjango => 950개 recovery, 여기 =>1406 . 또한 y,x로 되어있는데 x,y로 바꿔서 안돌리고 그냥 그대로 + 배열 reverse안하고 그냥 그대로 돌려도 잘 나옴
            '''
            old_vertex_recovery=[];ttl=[]
            print("start the init process")
            constants.temp_x, constants.temp_y, old_vertex_recovery, ttl = util.start_perbox(constants.old_vertex, old_vertex_recovery,constants.per_box_size, ttl)
            constants.user_ttl = util.start_with_user_vertex(constants.user_ttl)
            old_vertex_recovery, ttl = util.perbox_process(constants.old_vertex, old_vertex_recovery, ttl)
            print(len(old_vertex_recovery)) #여기까지가 346ms
            connectDB.save_DB_old_vertex(constants.new_uid, constants.old_vertex)
            connectDB.save_recovery_ttl(constants.new_uid, ttl)
            connectDB.save_DB_old_vertex_recovery(constants.new_uid, old_vertex_recovery)
            connectDB.save_user_ttl(constants.new_uid, constants.user_ttl,total_max_x,total_min_y)# 여기까지(recovery 5천개 넣는거 빼고)가 816ms
            '''
            return_status = 201;success = True;stat={"temp_x":total_max_x, "temp_y":total_min_y}

        data1 = {
                "success": success,
                "status": return_status,
                "data": stat
            }
        #constants.old_vertex_recovery=[];constants.ttl=[]
        return JsonResponse(data1, safe=False)


@csrf_exempt
def put(request):
    print("start the init process")
    old_vertex_recovery = [];    ttl = []
    data = JSONParser().parse(request)
    constants.new_uid = data['uid']
    constants.old_vertex = [tuple(data['safeZone'][k].values()) for k in range(len(data['safeZone']))]
    stat, total_max_x, total_min_y = vertify.zone_min_size(constants.old_vertex)
    constants.temp_x, constants.temp_y, old_vertex_recovery, ttl = util.start_perbox(constants.old_vertex,old_vertex_recovery,constants.per_box_size, ttl)
    constants.user_ttl = util.start_with_user_vertex(constants.user_ttl)
    old_vertex_recovery, ttl = util.perbox_process(constants.old_vertex, old_vertex_recovery, ttl)
    print(len(old_vertex_recovery))  # 여기까지가 346ms
    connectDB.save_DB_old_vertex(constants.new_uid, constants.old_vertex)
    connectDB.save_recovery_ttl(constants.new_uid, ttl)
    connectDB.save_DB_old_vertex_recovery(constants.new_uid, old_vertex_recovery)
    connectDB.save_user_ttl(constants.new_uid, constants.user_ttl, total_max_x,total_min_y)  # 여기까지(recovery 5천개 넣는거 빼고)가 816ms
    return_status = 201;    success = True;    stat = {"temp_x": total_max_x, "temp_y": total_min_y}
    data1 = {
        "success": success,
        "status": return_status,
        "data": stat
    }
    # constants.old_vertex_recovery=[];constants.ttl=[]
    return JsonResponse(data1, safe=False)


@csrf_exempt
def location_test(request):
    return_status = 204;success = False

    if request.method == 'POST':
        auth_token = request.headers.get("AccessToken", None)
        if auth_token == None:  # 토큰 값이 아예 안 들어왔을 때 401 코드 처리 및 메시지 출력
            return JsonResponse({'message': 'Enter the token.'}, status=401)
        '''
        padded = auth_token + "=" * divmod(len(auth_token), 4)[1]
        jsondata = base64.urlsafe_b64decode(padded)#현재 받은 토큰은, 손상된(변경된) 토큰임을 꼭 기억하기
        jsonbyte = bytearray(jsondata)
        cache_i1=0;cache_i2=0;count=0
        for i in range(len(jsonbyte)):
            if jsonbyte[i] == 34:                count+=1
            if count == 6:cache_i1=i
            if count == 8: cache_i2=i;break
        constants.new_uid = jsonbyte[cache_i1+2:cache_i2].decode('utf-8')
        '''
        # 받은 토큰 디코딩해서 user id 정보 출력하기
        jwt_options = {
            'verify_signature': False,
            'verify_exp': True,
            'verify_sub': True,
            'verify_nbf': False,
            'verify_iat': False,  # True,
            'verify_aud': False
        }
        try:
            jsondata = jwt.decode(auth_token, 'dkwndnlemal123!', algorithms=['HS256'], options=jwt_options)
        except:
            return JsonResponse({'message': 'token expired.'}, status=401)
        constants.new_uid =str(jsondata['sub'])

        data = JSONParser().parse(request)
        constants.new_data = tuple([data['latitude'] , data['longitude']])

        if (constants.cache_uid == constants.new_uid and ((abs(constants.new_data[0] - constants.prev_data[0]) < 0.00001 and abs(constants.new_data[1] - constants.prev_data[1] < 0.00001)))):
            print('same user: prev_data and new_data are too close');success = True
            data1 = {
                "success": success,
                "status": return_status,
                "data": 1
            }
            return JsonResponse(data1, safe=False)

        constants.ttl = connectDB.load_recovery_ttl(constants.new_uid)
        if (constants.cache_uid != constants.new_uid):#type(constants.ttl)==queryset , type(constants.old_vertex_recovery)=list
            print("user has been changed")
            if constants.cache_uid != 0:
                connectDB.save_variable_DB(constants.cache_uid, constants.per_box_size, constants.sum_dist, constants.count_t, constants.temp_x, constants.temp_y, constants.start_section)
            constants.cache_uid = constants.new_uid
            #ttl은 queryset형태. 파이썬 내부에서 수정 못하고 DB에 접근해서 수정해야함
            constants.old_vertex_recovery = connectDB.load_DB_old_vertex_recovery(constants.new_uid)
            constants.user_ttl, constants.per_box_size, constants.sum_dist, constants.count_t,constants.temp_x, constants.temp_y, constants.start_section = connectDB.load_variable_DB(constants.new_uid)
        safe_move=0
        us = User.objects.get(uid=constants.cache_uid)
        u = UserOption.objects.get(user_id=us.id)
        if u.safe_move == 1: safe_move=1

        print("user started process: ", datetime.now())
        # user ttl type check please###
        t = str(constants.user_ttl).split(' ')[0].split('-')  # old_vertex[-1].split('-')
        zone_mature_time = str(datetime.now() - datetime(int(t[0]), int(t[1]), int(t[2]))).split(' ')[0]
        # 이때 2021-10-02 - 2021-10-02가 되면(1일째의 경우) 시간만 남으므로 이때는 0으로 str처리해주기
        if zone_mature_time.find(':'): zone_mature_time = '0'

        #zone_mature_time='8'
        sendData = 0;status_sub = 0
        if (zone_mature_time <= '7'):  # use old_vertex #확대확대만 된다!: recovery배열을 보내줘야함 211002 => 2번검증하기!
            print('user zone_mature_time is lower than 7')
            status_sub, old_vertex_new = vertify.check_data_sub2(constants.new_data, constants.old_vertex_recovery, status_sub)

            if (status_sub == 1):  print('you are in safe_zone');sendData = 1;return_status=201;success=True
            elif (status_sub == 2):  # if totally outside, ⇒ rebuild safe_zone
                print('warning: you are location out of safe_zone')
                ttl_temp = 0
                old_vertex_new, ttl_temp = vertify.start_perbox_add(old_vertex_new, constants.new_data,constants.temp_x, constants.temp_y,constants.per_box_size, ttl_temp)
                constants.old_vertex_recovery.append(old_vertex_new)
                connectDB.save_recovery_ttl_one(constants.cache_uid, ttl_temp)
                connectDB.save_DB_old_vertex_recovery_one(constants.cache_uid, old_vertex_new)
                sendData = 2;return_status=201;success=True#old_vertex_new


        else:  # USE old_vertex_recovery
            status,constants.ttl = vertify.check_data_main(constants.new_data, constants.old_vertex_recovery, constants.status, constants.ttl, constants.cache_uid)
            sendData=1
            if (status == 1): print('you are in safe_zone');return_status=201;success=True
            elif (status == 2):
                print('warning: you are location out of safe_zone')# if outside ⇒ rebuild safe_zone
                old_vertex_new=0; ttl_temp=0
                old_vertex_new, ttl_temp = vertify.safe_zone_process(old_vertex_new,constants.new_data, constants.temp_x, constants.temp_y, constants.per_box_size,ttl_temp)
                constants.old_vertex_recovery.append(old_vertex_new)
                connectDB.save_recovery_ttl_one(constants.cache_uid, ttl_temp)
                connectDB.save_DB_old_vertex_recovery_one(constants.cache_uid, old_vertex_new)
                sendData=2;return_status=201;success=True

        constants.prev_data = constants.new_data
        if safe_move == 1: sendData=1
        data1 = {
            "success": success,
            "status": return_status,
            "data": sendData
        }
        return JsonResponse(data1, safe=False)


@csrf_exempt
def test_for_location(request):
    #위에서 얻어온 constants.new_uid를 기반으로
    temp_t=[]
    constants.old_vertex_recovery = connectDB.load_DB_old_vertex_recovery(constants.new_uid)
    local_tz = pytz.timezone("Asia/Seoul")
    converted_utc_dt = datetime.now() - timedelta(days=3)
    ttl = pytz.utc.localize(converted_utc_dt).astimezone(local_tz)
    print(ttl)
    te=User.objects.get(uid=constants.new_uid)

    for old in constants.old_vertex_recovery:
        x = (old[0][0]+old[3][0])/2;y = (old[0][1]+old[1][1])/2
        ttl = ttl + timedelta(seconds=10)
        temp_t.append(Location(created_at = ttl, latitude=x, longitude=y, user_id=te.id))

    Location.objects.bulk_create(temp_t, batch_size=999)
    data1 = {
        "success": 201,
        "status": True,
        "data": 1
    }
    print(len(temp_t))
    print(ttl)
    return JsonResponse(data1, safe=False)


@csrf_exempt
def con_test11(request):
    constants.cache_uid = 0
    print('shceduler update_safe_zone after Day 7')
    # 먼저 최소 size 검증을 진행하기 위해서 all_vertex를 DB에서 load
    a = UserOption.objects.filter(is_init_safe_zone__lt=1)
    print(len(a))

    for i in range(len(a)):
        temp = User.objects.get(id=a[i].user_id)
        uid = temp.uid
        t = str(temp.created_at).split(' ')[0].split('-')
        cloc = str(datetime.now() -datetime(int(t[0]), int(t[1]), int(t[2]))).split(' ')[0]

        #if cloc <= '7' or cloc.find(':') != -1: continue

        all_vertex = []
        all_vertex, constants.per_box_size, constants.sum_dist, constants.count_t = connectDB.load_DB_all_vertex(a[i].user_id)  # 8만개 data 효택 DB에서 load, 평균속도도 load
        constants.per_box_size = 100
        #constants.per_box_size = (constants.sum_dist / constants.count_t) * 90
        if len(all_vertex) == 0: continue
        stat, total_max_x, total_min_y = vertify.zone_min_size(all_vertex)

        if stat != 1: continue
        constants.old_vertex_recovery = [];constants.ttl = []
        constants.start_section = 1  # 8일이라고 8일에 갑자기 100회 이거 진행하는거 아니자나. 8일되었을때라도 딱 한번만 진행되어야하자나
        constants.temp_x, constants.temp_y, constants.old_vertex_recovery, constants.ttl = util.personal_box_first_time(
            constants.old_vertex_recovery, all_vertex, constants.per_box_size, constants.ttl, uid)

        print('user safe_zone update')
        connectDB.delete_all_recovery_ttl(a[i].user_id)
        #connectDB.delete_all_old_vertex_recovery(a[i].user_id)
        connectDB.save_recovery_ttl(uid, constants.ttl)
        connectDB.save_DB_old_vertex_recovery(uid, constants.old_vertex_recovery)
        connectDB.save_variable_DB(uid, constants.per_box_size, constants.sum_dist, constants.count_t,
                                   constants.temp_x, constants.temp_y, constants.start_section)
    data1 = {
        "success": 201,
        "status": True,
        "data": 1
    }
    return JsonResponse(data1, safe=False)


@csrf_exempt
def con_test22(request):
    constants.cache_uid = 0
    print('shceduler delete_expire_ttl after Day 7')
    a = UserOption.objects.filter(is_init_safe_zone__gt=0)
    print(len(a))

    for i in range(len(a)):
        # if a[i].is_init_safe_zone != 1: continue
        uid = User.objects.get(id=a[i].user_id).uid
        constants.ttl = connectDB.load_recovery_ttl(uid)
        constants.old_vertex_recovery = connectDB.load_DB_old_vertex_recovery(uid)
        constants.temp_x, constants.temp_y, constants.old_vertex_recovery, constants.ttl = util.personal_box_recovery_all_users(
            a[i].user_id, constants.old_vertex_recovery, constants.ttl)
        connectDB.save_variable_DB(uid, a[i].box_size, a[i].distance, a[i].time, constants.temp_x,
                                   constants.temp_y, a[i].is_init_safe_zone)
        # frontend에서는, 어차피 낮에 활동할때 바뀐 safe_zone에 대해서 내부외부 검증하고, 외부면 safe_zone 가져와서 그리므로, 따로 signal 안 보내줘도 괜찮음
    data1 = {
        "success": 201,
        "status": True,
        "data": 1
    }
    return JsonResponse(data1, safe=False)


@csrf_exempt
def for_predict_test(request):
    temp_t = []
    temp_id = User.objects.all().values_list('id', flat=True)
    temp_final = [[] for i in range(len(temp_id))]
    print(len(temp_id))

    old_vertex_recovery = connectDB.load_DB_old_vertex_recovery('ed4dba6f-cdd7-406e-8920-fe7d9afb62b8')
    local_tz = pytz.timezone("Asia/Seoul")
    ttl=[];converted_utc_dt = timezone.now()
    for i in range(30):
        if i == 0:
            kst = converted_utc_dt - timedelta(hours=10)#pytz.utc.localize(converted_utc_dt).astimezone(local_tz)
        kst = converted_utc_dt - timedelta(days=i)
        ttl.append(kst)
    print(ttl)
    for i in range(len(ttl)):
        for old in old_vertex_recovery:
            x = (old[0][0] + old[3][0]) / 2
            y = (old[0][1] + old[1][1]) / 2
            temp_t.append(Location(created_at=ttl[i], latitude=x, longitude=y))

    for i in range(len(temp_id)):
        temp_final[i] = copy.deepcopy(temp_t)

    for i in range(len(temp_id)):
        for bucket in temp_final[i]:
            bucket.user_id = temp_id[i]

    result = sum(temp_final, [])
    Location.objects.bulk_create(result, batch_size=999)
    data1 = {
        "success": 201,
        "status": True,
        "data": 1
    }
    print(len(result))
    return JsonResponse(data1, safe=False)


@csrf_exempt
def check_user(request):
    temp_id = User.objects.all().values_list('id', flat=True)
    temp_at = User.objects.all().values_list('created_at', flat=True)
    print(len(temp_id),len(temp_at))
    if len(temp_id)==0:
        dictionary=2
    else:
        dict_value = [{"id": temp_id[i], "created_at": temp_at[i]} for i in range(len(temp_id))]
        dictionary = {"all_user": dict_value}
    res_data = {
        "success": 201,
        "status": True,
        "data": dictionary
    }
    return JsonResponse(res_data, safe=False)


@csrf_exempt
def create_check(request,id):
    data=dict()
    temp=User.objects.all()
    print(len(temp))
    if len(temp)==0:
        data=2
    else:
        t = str(temp[id].created_at).split(' ')[0].split('-')
        cloc = str(datetime.now() - datetime(int(t[0]), int(t[1]), int(t[2]))).split(' ')[0]

        cloc='30'

        if cloc >= '29' and cloc.find(':') == -1:
            te, created_at = connectDB.load_DB_all_vertex2(temp[id].id)
            data['id']=temp[id].id
            data['gps']=te
            data['created_at'] = created_at
        else:
            data=2

    res_data = {
        "success": 201,
        "status": True,
        "data": data
    }
    print('django',id)
    return JsonResponse(res_data, safe=False)


@csrf_exempt
def test(request):
    data=dict()
    temp=[]
    temp=connectDB.load_DB_old_vertex_recovery('ed4dba6f-cdd7-406e-8920-fe7d9afb62b8')
    result = sum(temp, [])
    dict_value = [{"latitude": result[i][0], "longitude": result[i][1]} for i in range(len(result))]
    data['all_vertex'] = dict_value
    res_data = {
        "success": 201,
        "status": True,
        "data": data
    }
    return JsonResponse(res_data, safe=False)
