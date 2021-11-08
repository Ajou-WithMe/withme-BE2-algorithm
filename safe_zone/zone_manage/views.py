# Create your views here.

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.csrf import csrf_exempt
from .models import SafeZone, User, ZoneLocation,UserOption,Location, InitSafeZone
from .serializers import InitSafeZoneSer
from rest_framework.parsers import JSONParser
from . import connectDB, constants, vertify, util
import json,datetime, jwt, base64, struct


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
    return_status = 204;success = False
    old_vertex_recovery=[];ttl=[]

    if request.method == 'POST':
        auth_token = request.headers.get("AccessToken", None)

        # 토큰 값이 아예 안 들어왔을 때 401 코드 처리 및 메시지 출력
        if auth_token == None:
            return JsonResponse({'message': 'Enter the token.'}, status=401)
        # 받은 토큰 디코딩해서 user id 정보 출력하기
        #payload = jwt.decode(auth_token, SECRET,algorithm='HS256') #,algorithm='HS256' #ISO-8859-1 , euc-kr, cp949
        # uid = force_text(urlsafe_base64_decode(padded))  #print(int.from_bytes(jsondata, byteorder='big'))
        padded = auth_token + "=" * divmod(len(auth_token), 4)[1]
        jsondata = base64.urlsafe_b64decode(padded)
        jsonbyte = bytearray(jsondata)

        cache_i1=0;cache_i2=0;count=0
        for i in range(len(jsonbyte)):
            if jsonbyte[i] == 34:
                count+=1
            if count == 6:cache_i1=i
            if count == 8: cache_i2=i;break

        constants.new_uid = jsonbyte[cache_i1+2:cache_i2].decode('utf-8')

        data = JSONParser().parse(request)
        #constants.old_vertex, constants.new_uid =[tuple(data['safeZone'][k].values()) for k in range(len(data['safeZone']))], uid #str(uid)
        constants.old_vertex = [tuple(data['safeZone'][k].values()) for k in range(len(data['safeZone']))]
        stat, total_max_x, total_min_y = vertify.zone_min_size(constants.old_vertex) #여기까지가 20ms
        #print(stat)
        if stat == 1:  # 여기는 임시 변수만 사용하기.(새로운 유저들이 각자꺼만 저장해야하므로)
            #1101#geodjango => 950개 recovery, 여기 =>1406 . 또한 y,x로 되어있는데 x,y로 바꿔서 안돌리고 그냥 그대로 + 배열 reverse안하고 그냥 그대로 돌려도 잘 나옴
            print("start the init process")
            constants.temp_x, constants.temp_y, old_vertex_recovery, ttl = util.start_perbox(constants.old_vertex, old_vertex_recovery,constants.per_box_size, ttl)
            constants.user_ttl = util.start_with_user_vertex(constants.user_ttl)
            old_vertex_recovery, ttl = util.perbox_process(constants.old_vertex, old_vertex_recovery, ttl)
            print(len(old_vertex_recovery)) #여기까지가 346ms
            connectDB.save_DB_old_vertex(constants.new_uid, constants.old_vertex)
            connectDB.save_recovery_ttl(constants.new_uid, ttl)
            connectDB.save_DB_old_vertex_recovery(constants.new_uid, old_vertex_recovery)
            connectDB.save_user_ttl(constants.new_uid, constants.user_ttl,total_max_x,total_min_y)# 여기까지(recovery 5천개 넣는거 빼고)가 816ms
            return_status = 201;success = True;stat={"temp_x":total_max_x, "temp_y":total_min_y}
        data1 = {
                "success": success,
                "status": return_status,
                "data": stat
            }
        #constants.old_vertex_recovery=[];constants.ttl=[]
        return JsonResponse(data1, safe=False)


@csrf_exempt
def location_test(request):
    return_status = 204;success = False

    if request.method == 'POST':
        auth_token = request.headers.get("AccessToken", None)

        # 토큰 값이 아예 안 들어왔을 때 401 코드 처리 및 메시지 출력
        if auth_token == None:
            return JsonResponse({'message': 'Enter the token.'}, status=401)
        # 받은 토큰 디코딩해서 user id 정보 출력하기
        # payload = jwt.decode(auth_token, SECRET,algorithm='HS256') #,algorithm='HS256' #ISO-8859-1 , euc-kr, cp949
        # uid = force_text(urlsafe_base64_decode(padded))  #print(int.from_bytes(jsondata, byteorder='big'))
        padded = auth_token + "=" * divmod(len(auth_token), 4)[1]
        jsondata = base64.urlsafe_b64decode(padded)
        jsonbyte = bytearray(jsondata)

        cache_i1 = 0;cache_i2 = 0;count = 0
        for i in range(len(jsonbyte)):
            if jsonbyte[i] == 34:
                count += 1
            if count == 6: cache_i1 = i
            if count == 8: cache_i2 = i;break

        constants.new_uid = jsonbyte[cache_i1 + 2:cache_i2].decode('utf-8')

        data = JSONParser().parse(request)
        constants.new_data = tuple([data['latitude'] , data['longitude']])

        if (constants.cache_uid == constants.new_uid and ((abs(constants.new_data[0] - constants.prev_data[0]) < 0.00001 and abs(constants.new_data[1] - constants.prev_data[1] < 0.00001)))):
            print('same user: prev_data and new_data are too close')
            data1 = {
                "success": success,
                "status": return_status,
                "data": 1
            }
            return JsonResponse(data1, safe=False)

        if (constants.cache_uid != constants.new_uid):
            print("user has been changed")
            if constants.cache_uid != 0:
                connectDB.save_variable_DB(constants.cache_uid, constants.per_box_size, constants.sum_dist, constants.count_t, constants.temp_x, constants.temp_y, constants.start_section)
            constants.cache_uid = constants.new_uid
            constants.ttl= connectDB.load_recovery_ttl(constants.new_uid)
            #ttl은 queryset형태. 파이썬 내부에서 수정 못하고 DB에 접근해서 수정해야함
            constants.old_vertex_recovery = connectDB.load_DB_old_vertex_recovery(constants.new_uid)
            constants.user_ttl, constants.per_box_size, constants.sum_dist, constants.count_t,constants.temp_x, constants.temp_y, constants.start_section = connectDB.load_variable_DB(constants.new_uid)
        #print(constants.user_ttl, constants.per_box_size, constants.sum_dist, constants.count_t,constants.temp_x, constants.temp_y, constants.start_section)
        constants.per_box_size=100

        print("user started process: ", datetime.datetime.now())
        # user ttl type check please###
        t = str(constants.user_ttl).split(' ')[0].split('-')  # old_vertex[-1].split('-')
        zone_mature_time = str(datetime.datetime.now() - datetime.datetime(int(t[0]), int(t[1]), int(t[2]))).split(' ')[0]
        # 이때 2021-10-02 - 2021-10-02가 되면(1일째의 경우) 시간만 남으므로 이때는 0으로 str처리해주기
        if zone_mature_time.find(':'): zone_mature_time = '0'

        #zone_mature_time='8'
        sendData = 0;status_sub = 0
        if (zone_mature_time <= '7'):  # use old_vertex #확대확대만 된다!: recovery배열을 보내줘야함 211002 => 2번검증하기!
            print('user zone_mature_time is lower than 7')
            status_sub, old_vertex_new = vertify.check_data_sub2(constants.new_data, constants.old_vertex_recovery, status_sub)

            if (status_sub == 1):  print('you are in safe_zone');sendData = 1
            elif (status_sub == 2):  # if totally outside, ⇒ rebuild safe_zone
                print('warning: you are location out of safe_zone')
                ttl_temp = 0
                constants.old_vertex_recovery, old_vertex_new, ttl_temp = vertify.start_perbox_add(old_vertex_new, constants.new_data,constants.temp_x, constants.temp_y,constants.old_vertex_recovery,constants.per_box_size, ttl_temp)
                connectDB.save_recovery_ttl_one(constants.cache_uid, ttl_temp)
                connectDB.save_DB_old_vertex_recovery_one(constants.cache_uid, old_vertex_new)
                sendData = 2#old_vertex_new
                # return_status=201;success=True


        else:  # USE old_vertex_recovery
            status,constants.ttl = vertify.check_data_main(constants.new_data, constants.old_vertex_recovery, constants.status, constants.ttl, constants.cache_uid)
            sendData=1
            if (status == 1): print('you are in safe_zone')
            elif (status == 2):
                print('warning: you are location out of safe_zone')# if outside ⇒ rebuild safe_zone
                old_vertex_new=0; ttl_temp=0
                constants.old_vertex_recovery, old_vertex_new, ttl_temp = vertify.safe_zone_process(old_vertex_new,constants.new_data, constants.temp_x, constants.temp_y, constants.old_vertex_recovery, constants.per_box_size,ttl_temp)
                connectDB.save_recovery_ttl_one(constants.cache_uid, ttl_temp)
                connectDB.save_DB_old_vertex_recovery_one(constants.cache_uid, old_vertex_new)
                sendData=2;return_status=201;success=True
        constants.prev_data = constants.new_data
        data1 = {
            "success": success,
            "status": return_status,
            "data": sendData
        }
        return JsonResponse(data1, safe=False)