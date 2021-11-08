#종성 효택, spring 프레임워크 기반 DB 내용

import sqlite3, io, os, copy
#import django
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "safe_zone.settings")
#django.setup()
from .models import SafeZone, User, ZoneLocation,UserOption,Location, InitSafeZone
import numpy as np
import requests


def con_nect():
    User.objects.filter(id=1)
    return


def save_DB_old_vertex(new_uid,old_vertex):
    temp = User.objects.get(uid = new_uid)
    temp_t=[]
    for old in old_vertex:
        t = InitSafeZone(latitude=old[0], longitude=old[1], user_id= temp.id)
        temp_t.append(t)
    InitSafeZone.objects.bulk_create(temp_t)
    return


def save_recovery_ttl(new_uid,ttl):
    temp = User.objects.get(uid=new_uid)
    temp_t = []
    for old in ttl:
        t = SafeZone(ttl = old, user_id= temp.id)
        temp_t.append(t)
    SafeZone.objects.bulk_create(temp_t, batch_size=999)
    return


def save_DB_old_vertex_recovery(new_uid,old_vertex_recovery):#여기는 박스 전체를 저장하는, 그 user 최초recovery1 과 7일후 최초 recovery2에서 저장하는 거
    te = User.objects.get(uid=new_uid)
    temp = SafeZone.objects.filter(user_id=te.id).values_list('id',flat=True)   #temp에 idx가 다 담김
    temp_t = []
    count=-1
    #le = len(old_vertex_recovery)
    #for old_vertex in old_vertex_recovery: #2중 for문에서 시간 다 잡아먹음.
    #    count += 1
    #    for old in old_vertex:
    #        t = ZoneLocation(latitude=old[0], longitude=old[1], user_id=te.id,safe_zone_id=temp[count])
    #        temp_t.append(t)
    print(len(temp))
    for old_vertex in old_vertex_recovery:
        count += 1
        temp_t.extend([ZoneLocation(latitude=old[0], longitude=old[1], user_id=te.id,safe_zone_id=temp[count]) for old in old_vertex])
    #for i in range(le):
    #    temp_t.extend([ZoneLocation(latitude=old_vertex_recovery[i][j][0],longitude=old_vertex_recovery[i][j][1],user_id=te.id, safe_zone_id=temp[i]) for j in range(4)])
    print(len(temp_t))
    ZoneLocation.objects.bulk_create(temp_t, batch_size=999)
    #for i in range(0, 4 * le, 4):
    #    k=int(i/4)
    #    temp2[i].latitude, temp2[i].longitude = old_vertex_recovery[k][0][0], old_vertex_recovery[k][0][1]
    #    temp2[i + 1].latitude, temp2[i + 1].longitude = old_vertex_recovery[k][1][0], old_vertex_recovery[k][1][1]
    #    temp2[i + 2].latitude, temp2[i + 2].longitude = old_vertex_recovery[k][2][0], old_vertex_recovery[k][2][1]
    #    temp2[i + 3].latitude, temp2[i + 3].longitude = old_vertex_recovery[k][3][0], old_vertex_recovery[k][3][1]
    #ZoneLocation.objects.bulk_update(temp2, ['latitude', 'longitude'], batch_size=999)
    return


def save_user_ttl(new_uid, user_ttl,x_temp,y_temp):
    temp = User.objects.get(uid=new_uid)
    temp.created_at = user_ttl
    t = UserOption(is_init_safe_zone=0,push_alarm=0,safe_move=0,x_temp=x_temp,y_temp=y_temp,user_id=temp.id)
    temp.save()
    t.save()
    return


def save_variable_DB(cache_uid,per_box_size, sum_dist, count_t,temp_x, temp_y, start_section):
    temp = User.objects.get(uid=cache_uid)
    t = UserOption.objects.get(user_id=temp.id)
    t.box_size, t.is_init_safe_zone, t.x_temp, t.y_temp= per_box_size,start_section,temp_x,temp_y
    #t = UserOption(box_size= per_box_size, is_init_safe_zone=start_section, x_temp=temp_x,y_temp=temp_y,user_id=temp.id)
    t.save()
    return

'''
def load_user_ttl(cache_uid):
    temp = User.objects.get(uid=cache_uid)
    t = InitSafeZone.objects.filter(user_id=temp.id)
    return t[0].created_at
'''

def load_recovery_ttl(cache_uid):
    temp = User.objects.get(uid=cache_uid)
    t = SafeZone.objects.filter(user_id=temp.id).values_list('ttl', flat=True)
    print(len(t))
    return t


def load_DB_old_vertex_recovery(cache_uid):
    te = User.objects.get(uid=cache_uid)
    #temp = ZoneLocation.objects.filter(user_id=te.id)
    #latitude = temp.values_list('latitude', flat=True)
    #longitude = temp.values_list('longitude', flat=True)
    #temp = User.objects.get(uid=cache_uid)
    latitude = ZoneLocation.objects.filter(user_id=te.id).values_list('latitude', flat=True)
    longitude = ZoneLocation.objects.filter(user_id=te.id).values_list('longitude', flat=True)
    list_t=[]
    ls=[]
    count=0

    print(len(latitude),len(longitude))

    for i in range(len(latitude)):
        ls.append(tuple([latitude[i],longitude[i]]))
        count+=1
        if count==4:
            list_t.append(copy.deepcopy(ls))
            ls.clear()
            count=0
    return list_t


def load_variable_DB(cache_uid):
    temp = User.objects.get(uid=cache_uid)
    user_ttl = temp.created_at
    t = UserOption.objects.get(user_id = temp.id)

    per_box_size, sum_dist, count_t, temp_x, temp_y, start_section = t.box_size, t.distance,t.time, t.x_temp, t.y_temp, t.is_init_safe_zone
    return user_ttl,per_box_size, sum_dist, count_t,temp_x, temp_y, start_section


def save_recovery_ttl_one(cache_uid,ttl_temp):
    temp = User.objects.get(uid=cache_uid)
    t = SafeZone(ttl = ttl_temp, user_id=temp.id)
    t.save()
    return


def save_DB_old_vertex_recovery_one(cache_uid,old_vertex_new):#여기는 safe_zone 확대시 박스 1개
    te = User.objects.get(uid=cache_uid)
    temp = SafeZone.objects.filter(user_id=te.id).values_list('id', flat=True)
    print(len(temp))
    t=[]
    for old in old_vertex_new:
        t.append(ZoneLocation(latitude=old[0], longitude=old[1],user_id=te.id, safe_zone_id=temp[len(temp)-1]))
    ZoneLocation.objects.bulk_create(t)
    return


def load_DB_all_vertex(cache_uid):
    temp = User.objects.get(uid=cache_uid)
    latitude = Location.objects.filter(user_id=temp.id).values_list('latitude', flat=True)
    longitude = Location.objects.filter(user_id=temp.id).values_list('longitude', flat=True)
    print(len(latitude),len(longitude))
    ls=[]
    for i in range(len(latitude)):
        ls.append(tuple([latitude,longitude]))
    t = UserOption.objects.get(user_id=temp.id)
    return ls, t.box_size, t.distance, t.time


def delete_all_recovery_ttl(cache_uid):
    temp = User.objects.get(uid=cache_uid)
    SafeZone.objects.filter(user_id=temp.id).delete()
    return


def delete_all_old_vertex_recovery(cache_uid):
    te = User.objects.get(uid=cache_uid)
    temp = ZoneLocation.objects.filter(user_id=te.id).delete()#SafeZone.objects.filter(user_id=te.id).prefetch_related('id')
    return


def delete_ttl(cache_uid, old_vertex_delete):
    temp = User.objects.get(uid=cache_uid)
    t = SafeZone.objects.filter(user_id=temp.id)
    print(len(t))
    for idx in old_vertex_delete:
        t[idx].delete()
    return


def delete_DB_old_vertex_recovery(cache_uid, old_vertex_delete): #old_vertex_delete는 2차원 배열로 삭제할 perbox들 집합
    #cascade로 될테니까 너무 걱정 말구
    temp = User.objects.get(uid=cache_uid)
    t = ZoneLocation.objects.filter(user_id=temp.id)
    print(len(t))
    for idx in old_vertex_delete:
        t[idx].delete()
    return


def save_recovery_ttl_mod(cache_uid,value, ttl_temp):
    temp = User.objects.get(uid=cache_uid)
    t = SafeZone.objects.filter(user_id=temp.id)
    print(len(t))
    t[ttl_temp].ttl=value
    t[ttl_temp].save()
    return

'''
def save_snapshot_DB(cache_uid):
    # nd.array to text  when Insert DB, 아래 conn의 첫번째 인자는 db_name
    # + executeUpdate == modify
    def adapt_array(arr):
        out = io.BytesIO()
        np.save(out, arr)
        out.seek(0)
        return sqlite3.Binary(out.read())
    conn = sqlite3.connect('data', detect_types=sqlite3.PARSE_DECLTYPES)
    sqlite3.register_adapter(np.ndarray, adapt_array)
    return

def load_snapshot_DB(new_uid, text):
    # conn으로 DB 연결 + executeQuery == retrieve
    def convert_array(text):
        out = io.BytesIO(text)
        out.seek(0)
        return np.load(out)
    conn = sqlite3.connect('data', detect_types=sqlite3.PARSE_DECLTYPES)
    sqlite3.register_converter("array", convert_array)
    return

def save_most_DB(cache_uid,text):
    num = load_snapshot_DB(cache_uid, text)
    #conn으로 DB 연결하기
    #most 구간 저장하기
    return

def load_most_DB(new_uid):
    #conn=으로 DB 연결하기
    # most 구간 load하서 front에게 넘겨주기
    return
'''

