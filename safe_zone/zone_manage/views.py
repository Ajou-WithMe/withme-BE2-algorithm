# Create your views here.
import copy,requests

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.csrf import csrf_exempt
from .models import SafeZone, User, ZoneLocation,UserOption,Location, InitSafeZone ,VisitOften, PredictionLocation
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


#this part for checking  minimum size of user safe zone first time
@csrf_exempt
def Init_SafeZone(request):
    return_status = 204;success = False
    if request.method == 'POST':
        #we use JWT for authentication all user.
        auth_token = request.headers.get("AccessToken", None)
        #when user does not have token, we response with 401
        if auth_token == None:
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
        # decoding the token for get user uid
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
        print(str(jsondata['sub']))
        #constants.new_uid =str(jsondata['sub'])
        data = JSONParser().parse(request)
        #constants.old_vertex, constants.new_uid =[tuple(data['safeZone'][k].values()) for k in range(len(data['safeZone']))], uid #str(uid)
        old_vertex = [tuple(data['safeZone'][k].values()) for k in range(len(data['safeZone']))]
        stat, total_max_x, total_min_y = vertify.zone_min_size(old_vertex) #여기까지가 20ms

        if stat == 1:
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


#we disunite our safe zone checking section and insert section. here for insert
@csrf_exempt
def put(request):
    print("start the init process")
    old_vertex_recovery = [];    ttl = []
    data = JSONParser().parse(request)

    new_uid = data['uid']

    old_vertex = [tuple(data['safeZone'][k].values()) for k in range(len(data['safeZone']))]
    print(new_uid)
    #print(constants.old_vertex)
    stat, total_max_x, total_min_y = vertify.zone_min_size(old_vertex)

    #just make the hole square including all safe_zone vertices
    temp_x, temp_y, old_vertex_recovery, ttl = util.start_perbox(old_vertex,old_vertex_recovery,100.0, ttl)
    #user_ttl = util.start_with_user_vertex(constants.user_ttl)

    #and we renewing the square for checking inside of safe zone or remove other
    old_vertex_recovery, ttl = util.perbox_process(old_vertex, old_vertex_recovery, ttl)
    print(len(old_vertex_recovery))  # 여기까지가 346ms
    connectDB.save_DB_old_vertex(new_uid, old_vertex)
    connectDB.save_recovery_ttl(new_uid, ttl)
    connectDB.save_DB_old_vertex_recovery(new_uid, old_vertex_recovery)
    connectDB.save_user_ttl(new_uid, constants.user_ttl, total_max_x,total_min_y)  # 여기까지(recovery 5천개 넣는거 빼고)가 816ms
    return_status = 201;    success = True;    stat = {"temp_x": total_max_x, "temp_y": total_min_y}
    data1 = {
        "success": success,
        "status": return_status,
        "data": stat
    }
    # constants.old_vertex_recovery=[];constants.ttl=[]
    return JsonResponse(data1, safe=False)


#and then, checking GPS data for all user periodically every 5 seconds
@csrf_exempt
def location_test(request):
    return_status = 204;success = False

    if request.method == 'POST':
        # we use JWT for authentication all user.
        auth_token = request.headers.get("AccessToken", None)
        # when user does not have token, we response with 401
        if auth_token == None:
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
        # decoding the token for get user uid
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
        new_uid =str(jsondata['sub'])

        data = JSONParser().parse(request)
        new_data = tuple([data['latitude'] , data['longitude']])


        #we check this special case for twice. first in here, and second in MYSQL DB
        #user can stay same area(cafe or school class room etc). when insert same GPS data many time like this situations, we can not check precise user speed
        if (constants.cache_uid == new_uid and ((abs(new_data[0] - constants.prev_data[0]) < 0.00001 and abs(new_data[1] - constants.prev_data[1] < 0.00001)))):
            print('same user: prev_data and new_data are too close');success = True
            #print('-------------uid: ', new_uid, '-------------')
            #print('-------------', [data['latitude'], data['longitude']], '-------------')
            data1 = {
                "success": success,
                "status": return_status,
                "data": 1
            }
            return JsonResponse(data1, safe=False)
        ttl=[];old_vertex_recovery=[]; user_ttl=0;safe_move=0
        ttl = connectDB.load_recovery_ttl(new_uid)
        constants.cache_uid = new_uid
        old_vertex_recovery = connectDB.load_DB_old_vertex_recovery(new_uid)
        user_ttl, per_box_size, sum_dist, count_t, temp_x, temp_y, start_section = connectDB.load_variable_DB(new_uid)
        us = User.objects.get(uid=new_uid)
        u = UserOption.objects.get(user_id=us.id)
        if u.safe_move == 1: safe_move=1

        print("user started process: ", datetime.now())
        # we use user created time for check before 7 days or another
        t = str(user_ttl).split(' ')[0].split('-')  # old_vertex[-1].split('-')
        zone_mature_time = str(datetime.now() - datetime(int(t[0]), int(t[1]), int(t[2]))).split(' ')[0]
        # when calculate 2021-10-02 - 2021-10-02 result is remain __:__:__ (just time, not day), so we setting this variable for 0(str)
        if zone_mature_time.find(':'): zone_mature_time = '0'

        #zone_mature_time='8'#for testing
        sendData = 0;status_sub = 0
        if (zone_mature_time <= '7'):
            print('user zone_mature_time is lower than 7')
            status_sub, old_vertex_new = vertify.check_data_sub2(new_data, old_vertex_recovery, status_sub)

            if (status_sub == 1):  print('you are in safe_zone');sendData = 1;return_status=201;success=True
            elif (status_sub == 2):  # if totally outside, ⇒ rebuild safe_zone
                print('warning: you are location out of safe_zone')
                ttl_temp = 0
                old_vertex_new, ttl_temp = vertify.start_perbox_add(old_vertex_new, new_data,temp_x, temp_y,per_box_size, ttl_temp)
                old_vertex_recovery.append(old_vertex_new)
                connectDB.save_recovery_ttl_one(new_uid, ttl_temp)
                connectDB.save_DB_old_vertex_recovery_one(new_uid, old_vertex_new)
                sendData = 2;return_status=201;success=True#old_vertex_new


        else:  # USE old_vertex_recovery
            status=0
            status,ttl = vertify.check_data_main(new_data, old_vertex_recovery, status, ttl, new_uid)
            sendData=1
            if (status == 1): print('you are in safe_zone');return_status=201;success=True
            elif (status == 2):
                print('warning: you are location out of safe_zone')# if outside ⇒ rebuild safe_zone
                old_vertex_new=0; ttl_temp=0
                old_vertex_new, ttl_temp = vertify.safe_zone_process(old_vertex_new,new_data, temp_x, temp_y, per_box_size,ttl_temp)
                old_vertex_recovery.append(old_vertex_new)
                connectDB.save_recovery_ttl_one(new_uid, ttl_temp)
                connectDB.save_DB_old_vertex_recovery_one(new_uid, old_vertex_new)
                sendData=2;return_status=201;success=True
        connectDB.save_variable_DB(new_uid, per_box_size, sum_dist, count_t,temp_x, temp_y, start_section)

        constants.prev_data = new_data
        if safe_move == 1: sendData=1
        data1 = {
            "success": success,
            "status": return_status,
            "data": sendData
        }
        #print('-------------uid: ', new_uid, '-------sendData: ',sendData)
        #print('-------------', [data['latitude'], data['longitude']], '-------------')

        return JsonResponse(data1, safe=False)


@csrf_exempt
def test_for_location(request,uid):
    #위에서 얻어온 constants.new_uid를 기반으로
    temp_t=[]
    constants.old_vertex_recovery = connectDB.load_DB_old_vertex_recovery(uid)#('ed4dba6f-cdd7-406e-8920-fe7d9afb62b8')#(constants.new_uid)
    local_tz = pytz.timezone("Asia/Seoul")
    converted_utc_dt = datetime.now() - timedelta(days=3)
    ttl = pytz.utc.localize(converted_utc_dt).astimezone(local_tz)
    print(ttl)
    te=User.objects.get(uid=uid)#(uid=constants.new_uid)
    print('id is ', te.id)
    for old in constants.old_vertex_recovery:
        x = (old[0][0]+old[3][0])/2;y = (old[0][1]+old[1][1])/2
        ttl = ttl + timedelta(seconds=10)
        temp_t.append(Location(created_at = ttl, latitude=x, longitude=y, user_id=te.id))

    for old in constants.old_vertex_recovery[:int(len(constants.old_vertex_recovery)/2)+1]:
        x = (old[0][0]+old[3][0])/2;y = (old[0][1]+old[1][1])/2
        ttl = ttl + timedelta(seconds=10)
        temp_t.append(Location(created_at = ttl, latitude=x, longitude=y, user_id=te.id))

    for old in constants.old_vertex_recovery[:int(len(constants.old_vertex_recovery)/3)+1]:
        x = (old[0][0]+old[3][0])/2;y = (old[0][1]+old[1][1])/2
        ttl = ttl + timedelta(seconds=10)
        temp_t.append(Location(created_at = ttl, latitude=x, longitude=y, user_id=te.id))

    for old in constants.old_vertex_recovery[:int(len(constants.old_vertex_recovery) / 5) + 1]:
        x = (old[0][0] + old[3][0]) / 2;        y = (old[0][1] + old[1][1]) / 2
        ttl = ttl + timedelta(seconds=10)
        temp_t.append(Location(created_at=ttl, latitude=x, longitude=y, user_id=te.id))

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
def update_safe_zone(request):
    constants.cache_uid = 0
    print('shceduler update_safe_zone after Day 7')
    # access DB for loading all vertex, because of checking minimum size of safe_zone.
    # when is_init_safe_zone flag is 0, we can start this part(if not 0, your are pass this part before)
    a = UserOption.objects.filter(is_init_safe_zone__lt=1)
    print(len(a))

    for i in range(len(a)):
        temp = User.objects.get(id=a[i].user_id)
        uid = temp.uid
        t = str(temp.created_at).split(' ')[0].split('-')
        cloc = str(datetime.now() - datetime(int(t[0]), int(t[1]), int(t[2]))).split(' ')[0]

        #you can enter here when you create your user before 7 days. check the date is correct, and processing next step
        if cloc <= '7' or cloc.find(':') != -1: continue

        all_vertex = []
        all_vertex, per_box_size, sum_dist, count_t = connectDB.load_DB_all_vertex(a[i].user_id)

        #we created per_box_size for all user's dynamic size. but, in initial model, we keep this variable fixed.
        per_box_size = 100
        # per_box_size = (constants.sum_dist / constants.count_t) * 90
        if len(all_vertex) == 0: continue
        #check zone minimum size is very important because of reducing the error of user life radius.
        stat, total_max_x, total_min_y = vertify.zone_min_size(all_vertex)
        print('result is ',stat)

        if stat != 1: continue
        old_vertex_recovery = [];        ttl = []
        # if you pass all checking session, you can enter renewing all safezone perboxes step. so setting is_init_safe_zone =1
        start_section = 1
        temp_x, temp_y, old_vertex_recovery, ttl = util.personal_box_first_time(old_vertex_recovery, all_vertex, per_box_size, ttl, uid)

        print('user safe_zone update')
        connectDB.delete_all_recovery_ttl(a[i].user_id)
        connectDB.save_recovery_ttl(uid, ttl)
        connectDB.save_DB_old_vertex_recovery(uid, old_vertex_recovery)
        connectDB.save_variable_DB(uid, per_box_size, sum_dist, count_t,temp_x, temp_y, start_section)
    data1 = {
        "success": 201,
        "status": True,
        "data": 1
    }
    return JsonResponse(data1, safe=False)


@csrf_exempt
def delete_expire_ttl(request):
    constants.cache_uid = 0
    print('shceduler delete_expire_ttl after Day 7')
    #you can enter this session when is_init_safe_zone variable = 1. that means the user are created after day 7.
    #so they are ready for delete expired ttl
    a = UserOption.objects.filter(is_init_safe_zone__gt=0)
    print(len(a))

    for i in range(len(a)):
        ttl=[];old_vertex_recovery=[]
        # if a[i].is_init_safe_zone != 1: continue
        uid = User.objects.get(id=a[i].user_id).uid
        ttl = connectDB.load_recovery_ttl(uid)
        old_vertex_recovery = connectDB.load_DB_old_vertex_recovery(uid)
        temp_x, temp_y, old_vertex_recovery, ttl = util.personal_box_recovery_all_users(a[i].user_id, old_vertex_recovery, ttl)
        connectDB.save_variable_DB(uid, a[i].box_size, a[i].distance, a[i].time, temp_x,temp_y, a[i].is_init_safe_zone)


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

    old_vertex_recovery = connectDB.load_DB_old_vertex_recovery('4fd5da53-2181-40c8-a31c-30785de3c5d1')
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

        #cloc='30'#지우기

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
def visit_often(request,id):#여기로 요청이 들어온다는건, 기존이 해당 id로 된 data가 VisitOften테이블에 있으면 안된다는거!!!
    data=dict()
    temp = User.objects.all()
    print(len(temp))
    if len(temp) == 0:
        data = 2
    else:
        te = connectDB.load_DB_all_vertex3(temp[id].id)
        if te['all_vertex'] == 2: data=2
        else:
            VisitOften.objects.filter(user_id=temp[id].id).delete()
            data['id'] = temp[id].id
            data['gps']=te

    res_data = {
        "success": 201,
        "status": True,
        "data": data
    }
    return JsonResponse(res_data, safe=False)


#VisitOften, #latitude longitude grade user_id
@csrf_exempt
def visit_often_put(request,id):
    data = JSONParser().parse(request)
    temp_t=[]
    if data['flag'] == 0:
        for old_vertex in data["all_zone"]:
            temp_t.extend([VisitOften(latitude=old[0], longitude=old[1], grade= data['grade'][0], user_id=id) for old in old_vertex])
    else:
        count=0; c_count=0; cache_count=0
        for old_vertex in data["all_zone"]:
            if c_count<3:
                if count == data['flag'][c_count]:
                    cache_count=c_count;c_count+=1
            temp_t.extend([VisitOften(latitude=old[0], longitude=old[1], grade=data['grade'][cache_count], user_id=id) for old in old_vertex])
            count+=1
    VisitOften.objects.bulk_create(temp_t, batch_size=999)

    res_data = {
        "success": 201,
        "status": True,
        "data": 1
    }
    return JsonResponse(res_data, safe=False)


@csrf_exempt
def make_model(request,id):
    data = dict()
    temp = User.objects.all()
    print(len(temp))
    if len(temp) == 0:
        data = 2
    else:
        te = connectDB.load_DB_all_vertex3(temp[id].id)
        if te['all_vertex'] == 2:
            data = 2
        else:
            data['id'] = temp[id].id
            data['gps'] = te
    res_data = {
        "success": 201,
        "status": True,
        "data": data
    }
    return JsonResponse(res_data, safe=False)


@csrf_exempt
def search_for_prediction(request,id):
    # you are in crontab
    # you save prediction boxes in mysql prediction_location_table
    temp = User.objects.all()
    print(len(temp))
    if len(temp) == 0:
        data = 2
    else:
        for i in range(len(temp)):
            try:
                t = UserOption.objects.get(user_id=temp[i].id)
            except:
                print('that user are error about something')
                continue
            if t.is_disconnected:
                find_xy = Location.objects.filter(user_id=temp[i].id)
                if len(find_xy) < 1: continue
                find_x=find_xy[len(find_xy)-1].latitude
                find_y=find_xy[len(find_xy)-1].longitude

                res0 = requests.get('http://3.37.163.203:8040/zone_manage/certify_make_model/' + str(i) + '/')
                re0 = res0.json()
                temp_t = re0['data']
                if temp_t == 2:  continue  # 예외처리

                URL = 'http://3.37.163.203:8080/prediction/certify_predict/'+str(temp[i].id)+'/?username=withmeuser&password=adminuser'
                req_data = {'temp':{'temp_x': t.x_temp, 'temp_y': t.y_temp}, 'last':{'last_x':find_x, 'last_y':find_y,}, 'data_train': temp_t['gps']}
                res = requests.post(URL, data=json.dumps(req_data))
                re = res.json()
                te = re['data']
                if te == 2:  continue

                else:
                    temp_t=[]
                    local_tz = pytz.timezone("Asia/Seoul")
                    converted_utc_dt = datetime.now()
                    tt = pytz.utc.localize(converted_utc_dt).astimezone(local_tz)
                    Location(created_at=tt, latitude=re['predict']['latitude'], longitude=re['predict']['longitude'], user_id=temp[i].id).save()
                    data_value = [tuple(te[k].values()) for k in range(len(te))]
                    temp_t.extend([PredictionLocation(latitude=old[0], longitude=old[1], user_id=temp[i].id) for old in data_value])
                    PredictionLocation.objects.bulk_create(temp_t, batch_size=999)

    res_data = {
        "success": 201,
        "status": True,
        "data": 1
    }
    return JsonResponse(res_data, safe=False)


@csrf_exempt
def test(request):
    data={}
    latitude = PredictionLocation.objects.filter(user_id=87).values_list('latitude', flat=True)
    longitude = PredictionLocation.objects.filter(user_id=87).values_list('longitude', flat=True)
    print(len(latitude), len(longitude))
    dict_value = [{"latitude": latitude[i], "longitude": longitude[i]} for i in range(len(latitude))]
    dictionary = {"all_vertex": dict_value}
    data['gps'] = dictionary
    res_data = {
        "success": 201,
        "status": True,
        "data": data
    }
    return JsonResponse(res_data, safe=False)

