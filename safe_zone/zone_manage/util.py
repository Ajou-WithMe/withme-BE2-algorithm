"""
made by BaekJongSeong
util for
safe_zone production,
safe_zone enlargement/reduction,
data TTL calculation,
"""

from datetime import datetime, timedelta
from django.utils import timezone
from . import vertify,connectDB
import pytz,copy
import numpy as np


def start_with_user_vertex(user_ttl):
    user_ttl = timezone.now().astimezone() # 처음 받아온 날짜 append 했으니, 앞으로는 그시점 날짜 - 이날짜 해서 7일 오바되었다???로 계산
    return user_ttl


def find_minmax_vertex(all_vertex): # 전체 vertex에서 가장 좌측 최상단 좌표 뽑아내기 위함
    coordi_sort1 = sorted(all_vertex, key=lambda x: (x[0]))
    coordi_sort2 = sorted(all_vertex, key=lambda x: (x[1]))
    return coordi_sort1[0][0], coordi_sort2[0][1], coordi_sort1[-1][0], coordi_sort2[-1][1], coordi_sort1


def start_perbox(old_vertex,old_vertex_recovery,per_box_size,ttl):
    total_min_x, total_min_y, total_max_x, total_max_y, coordi_sort1 = find_minmax_vertex(old_vertex)
    temp_x = total_max_x  # frontemd에서 좌표 받아오면 전체 safe_zone에 대한 꼭지점임. 개개인 박스 꼭짓점이 아니고!!
    temp_y = total_min_y  # 내가 personal_box 사이즈로 나눠서 어짜피 좌표 다 하나씩 일일히 추가해야함
    per_box = per_box_size / 100000
    digit = len(str(per_box)) - 2
    local_tz = pytz.timezone("Asia/Seoul")
    converted_utc_dt = datetime.now() + timedelta(days=1)
    tt = pytz.utc.localize(converted_utc_dt).astimezone(local_tz)

    t_x = temp_x
    while True:
        t_y = temp_y
        if (t_x <= total_min_x): break  # 이 말은 다음 경우 포함. x=-10인데, 박스 만들라보니까 마지막 박스가x=-9~-12로 됨. 즉 -10인 원래 경계는 오바했으나, 박스 하나 추가되면서 끝나는거므로 ㅇ
        while True:  # 이 말은 다음 경우 포함. y=10인데, 박스 만들라보니까 마지막 박스가y=9~12로 됨. 즉 10인 원래 경계는 오바했으나, 박스 하나 추가되면서 끝나는거므로 ㅇㅋ
            if (t_y >= total_max_y): break
            temp = []
            t_xx = round(t_x,digit);t_yy = round(t_y,digit);t_xx_per = round(t_x - per_box,digit);t_yy_per = round(t_y + per_box,digit)
            temp.append((t_x, t_y))
            temp.append((t_x, t_y + per_box))
            temp.append((t_x - per_box, t_y + per_box))
            temp.append((t_x - per_box, t_y))
            ttl.append(tt)#temp.append(0) #old_vertex에 포함되어있지 않다는 소리!!!!
            #ttl.append(0)
            old_vertex_recovery.append(temp)
            t_y = t_y + per_box
        t_x = t_x - per_box

    return temp_x, temp_y, old_vertex_recovery,ttl #좌표 4개씩으로 된거만 추가되어있고, 시간ttl은 없다!!


def perbox_process(old_vertex,old_vertex_recovery,ttl):
    return vertify.check_data_special(old_vertex,old_vertex_recovery,ttl)


def ttl_update(ttl): #ttl형식 2021-07-19
    local_tz = pytz.timezone("Asia/Seoul")
    if ttl == '0':  # 초기상태이므로
        return ttl        #ttl=pytz.utc.localize(converted_utc_dt).astimezone(local_tz)#timezone.now().astimezone()+ timedelta(days=1) #ttl = str(datetime.now() + timedelta(days=1)).split(' ')[0]
    else:
        t = str(ttl).split(' ')[0].split('-')
        cloc= str(datetime(int(t[0]), int(t[1]), int(t[2])) - datetime.now()).split(' ')[0]
        if cloc < '7' or cloc.find(':')!=-1:
            converted_utc_dt = datetime(int(t[0]), int(t[1]), int(t[2]),tzinfo=pytz.UTC) + timedelta(days=1) #str(datetime(int(t[0]), int(t[1]), int(t[2])) + timedelta(days=1)).split(' ')[0]
            ttl = pytz.utc.localize(converted_utc_dt).astimezone(local_tz)
    return ttl


def check_it(temp_x,temp_y,per_box_size,new_data,c_count):
    per_box = per_box_size / 100000
    count_x=0;count_y=0
    t_x = temp_x
    while True:
        if (t_x - per_box < new_data[0]): break
        t_x = t_x - per_box
        count_x+=1
    t_y = temp_y
    while True:
        if (t_y + per_box > new_data[1]): break
        t_y = t_y + per_box
        count_y+=1
    return count_y+(count_x*c_count)


def personal_box_recoverying(temp_x,temp_y,per_box_size,c_count,coordi_sort1 , old_vertex_recovery,ttl,cache_uid): #old_vertex_recovery 얘도 현재 x[0], x[1] 오름차순으로 정렬되어있겠지요~
    coordi_sort1 = sorted(coordi_sort1, key=lambda x: (x[0], x[1]))
    status=0;temp_t=[]
    local_tz = pytz.timezone("Asia/Seoul")
    converted_utc_dt = datetime.now() + timedelta(days=1)
    #converted_utc_dt = datetime.now() - timedelta(days=2) #==> 테스트용
    ttl_t = pytz.utc.localize(converted_utc_dt).astimezone(local_tz)

    for vertex in coordi_sort1:
        id=check_it(temp_x, temp_y, per_box_size, vertex, c_count)
        status = vertify.check_data_main(vertex, [old_vertex_recovery[id]], status, '0', cache_uid)
        if status == 1:
            temp_t.append(id)

    temp_t=list(set(temp_t))
    ttl = [ttl_t]*len(temp_t)
    print(len(temp_t))
    old_vertex_recovery_new=[]
    for i in temp_t:
        old_vertex_recovery_new.append(old_vertex_recovery[i])
    print('old_vertex_recovery_new',len(old_vertex_recovery_new))
    return old_vertex_recovery_new, ttl


def personal_box_first_time(old_vertex_recovery, all_vertex, per_box_size,ttl,cache_uid):
    total_min_x, total_min_y, total_max_x, total_max_y, coordi_sort1 = find_minmax_vertex(all_vertex)
    temp_x = total_max_x #frontemd에서 좌표 받아오면 전체 safe_zone에 대한 꼭지점임. 개개인 박스 꼭짓점이 아니고!!
    temp_y = total_min_y #내가 personal_box 사이즈로 나눠서 어짜피 좌표 다 하나씩 일일히 추가해야함
    per_box = per_box_size / 100000
    digit = len(str(per_box)) - 2
    t_x = temp_x;c_count=0
    while True:
        t_y = temp_y
        cc_count=0
        if (t_x <= total_min_x): break #이 말은 다음 경우 포함. x=-10인데, 박스 만들라보니까 마지막 박스가x=-9~-12로 됨. 즉 -10인 원래 경계는 오바했으나, 박스 하나 추가되면서 끝나는거므로 ㅇ
        while True: #이 말은 다음 경우 포함. y=10인데, 박스 만들라보니까 마지막 박스가y=9~12로 됨. 즉 10인 원래 경계는 오바했으나, 박스 하나 추가되면서 끝나는거므로 ㅇㅋ
            if (t_y >= total_max_y): break
            temp = []
            t_xx = round(t_x, digit);t_yy = round(t_y, digit);t_xx_per = round(t_x - per_box, digit);t_yy_per = round(t_y + per_box, digit)
            temp.append((t_x, t_y))
            temp.append((t_x, t_y + per_box))
            temp.append((t_x - per_box, t_y + per_box))
            temp.append((t_x - per_box, t_y))
            ttl.append('0')
            old_vertex_recovery.append(temp)
            t_y = t_y + per_box
            cc_count+=1

        t_x = t_x - per_box
        c_count=cc_count

    old_vertex_recovery,ttl = personal_box_recoverying(temp_x,temp_y,per_box_size,c_count,coordi_sort1, old_vertex_recovery, ttl,cache_uid)
    return temp_x, temp_y, old_vertex_recovery,ttl


def personal_box_recovery_all_users(user_id,old_vertex_recovery,ttl):
    temp=[];temp_t=[];count=0
    #old = np.array(old_vertex_recovery).flatten().tolist()
    old = sum(old_vertex_recovery, [])

    for zone in old_vertex_recovery:
        t = str(ttl[old_vertex_recovery.index(zone)]).split(' ')[0].split('-')
        cloc= str(datetime.now() - datetime(int(t[0]), int(t[1]), int(t[2]))).split(' ')[0]
        if cloc > '0' or cloc.find(':')!=-1:
            count+=1
            if count % 50 == 0:
                stat, total_max_x, total_min_y = vertify.zone_min_size(old)
                if stat != 1: break
                else:
                    temp.extend(copy.deepcopy(temp_t))
                    temp_t.clear()

            temp_t.append(old_vertex_recovery.index(zone))
            for z in zone:
                old.remove(z)

    print(len(temp), 'will be removed in',user_id)

    temp.sort(reverse = True)  #뒤에 index 부터 지우게
    if len(temp) != 0:
        connectDB.delete_ttl(user_id, temp)
        #connectDB.delete_DB_old_vertex_recovery(user_id, temp) => 자동으로 관련된 old_vertex_recovery cascade로 지워지넹

    max_x = 0; max_y = 0; min_x = 200; min_y = 200
    for vertex in old_vertex_recovery:
        if (vertex[0][0] > max_x): max_x = vertex[0][0]  # 좌표순서는 1(좌측최상단) 2 3 4(좌측최하단)
        if (vertex[0][1] < min_y): min_y = vertex[0][1]

    return max_x, min_y, old_vertex_recovery, ttl