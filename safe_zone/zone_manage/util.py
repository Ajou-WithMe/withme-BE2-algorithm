from datetime import datetime, timedelta
from django.utils import timezone
from . import vertify,connectDB
import pytz
#from con_project.project import connectDB


def start_with_user_vertex(user_ttl):
    user_ttl = timezone.now()  # 처음 받아온 날짜 append 했으니, 앞으로는 그시점 날짜 - 이날짜 해서 7일 오바되었다???로 계산
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
    t_x = temp_x
    while True:
        t_y = temp_y
        if (t_x <= total_min_x): break  # 이 말은 다음 경우 포함. x=-10인데, 박스 만들라보니까 마지막 박스가x=-9~-12로 됨. 즉 -10인 원래 경계는 오바했으나, 박스 하나 추가되면서 끝나는거므로 ㅇ
        while True:  # 이 말은 다음 경우 포함. y=10인데, 박스 만들라보니까 마지막 박스가y=9~12로 됨. 즉 10인 원래 경계는 오바했으나, 박스 하나 추가되면서 끝나는거므로 ㅇㅋ
            if (t_y >= total_max_y): break
            temp = []
            t_xx = round(t_x,digit);t_yy = round(t_y,digit);t_xx_per = round(t_x - per_box,digit);t_yy_per = round(t_y + per_box,digit)
            temp.append((t_xx, t_yy))
            temp.append((t_xx, t_yy_per))
            temp.append((t_xx_per, t_yy_per))
            temp.append((t_xx_per, t_yy))
            ttl.append(timezone.now() + timedelta(days=1))#temp.append(0) #old_vertex에 포함되어있지 않다는 소리!!!!
            #ttl.append(0)
            old_vertex_recovery.append(temp)
            t_y = t_y + per_box
        t_x = t_x - per_box
    return temp_x, temp_y, old_vertex_recovery,ttl #좌표 4개씩으로 된거만 추가되어있고, 시간ttl은 없다!!


def perbox_process(old_vertex,old_vertex_recovery,ttl):
    return vertify.check_data_special(old_vertex,old_vertex_recovery,ttl)


def ttl_update(ttl): #ttl형식 2021-07-19
    if ttl == '0':  # 초기상태이므로
        ttl=timezone.now() #ttl = str(datetime.now() + timedelta(days=1)).split(' ')[0]

    else:
        t = str(ttl).split(' ')[0].split('-')
        cloc= str(datetime(int(t[0]), int(t[1]), int(t[2])) - datetime.now()).split(' ')[0]
        if str(cloc) < '7' or str(cloc).find(':'):
            KST = pytz.timezone('Asia/Seoul')
            ttl = datetime(int(t[0]), int(t[1]), int(t[2]),tzinfo=KST) + timedelta(days=1) #str(datetime(int(t[0]), int(t[1]), int(t[2])) + timedelta(days=1)).split(' ')[0]
            print(ttl)
    return ttl


def personal_box_recoverying(coordi_sort1 , old_vertex_recovery,ttl,cache_uid): #old_vertex_recovery 얘도 현재 x[0], x[1] 오름차순으로 정렬되어있겠지요~
    coordi_sort1 = sorted(coordi_sort1, key=lambda x: (x[0], x[1]))
    status=0
    for vertex in coordi_sort1:
        count = 0
        for zone in old_vertex_recovery:
            temp=[]; temp.append(zone)
            status,ttl[old_vertex_recovery.index(zone)] = vertify.check_data_main(vertex, temp, status,old_vertex_recovery.index(zone),cache_uid)
            if status == 1: break
            count += 1

    for zone in old_vertex_recovery:
        if ttl[old_vertex_recovery.index(zone)] == '0':
            del ttl[old_vertex_recovery.index(zone)]
            old_vertex_recovery.remove(zone)

    return old_vertex_recovery, ttl


def personal_box_first_time(old_vertex_recovery, all_vertex, per_box_size,ttl,cache_uid):
    old_vertex_recovery=[]
    ttl=[]
    total_min_x, total_min_y, total_max_x, total_max_y, coordi_sort1 = find_minmax_vertex(all_vertex)
    temp_x = total_max_x #frontemd에서 좌표 받아오면 전체 safe_zone에 대한 꼭지점임. 개개인 박스 꼭짓점이 아니고!!
    temp_y = total_min_y #내가 personal_box 사이즈로 나눠서 어짜피 좌표 다 하나씩 일일히 추가해야함
    per_box = per_box_size / 100000
    digit = len(str(per_box)) - 2
    t_x = temp_x
    while True:
        t_y = temp_y
        if (t_x <= total_min_x): break #이 말은 다음 경우 포함. x=-10인데, 박스 만들라보니까 마지막 박스가x=-9~-12로 됨. 즉 -10인 원래 경계는 오바했으나, 박스 하나 추가되면서 끝나는거므로 ㅇ
        while True: #이 말은 다음 경우 포함. y=10인데, 박스 만들라보니까 마지막 박스가y=9~12로 됨. 즉 10인 원래 경계는 오바했으나, 박스 하나 추가되면서 끝나는거므로 ㅇㅋ
            if (t_y >= total_max_y): break
            temp = []
            t_xx = round(t_x, digit);t_yy = round(t_y, digit);t_xx_per = round(t_x - per_box, digit);t_yy_per = round(t_y + per_box, digit)
            temp.append((t_xx, t_yy))
            temp.append((t_xx, t_yy_per))
            temp.append((t_xx_per, t_yy_per))
            temp.append((t_xx_per, t_yy))
            ttl.append('0')
            old_vertex_recovery.append(temp)
            t_y = t_y + per_box

        t_x = t_x - per_box

    old_vertex_recovery,ttl = personal_box_recoverying(coordi_sort1, old_vertex_recovery, ttl,cache_uid)
    return temp_x, temp_y, old_vertex_recovery,ttl


def personal_box_recovery_all_users(cache_uid,old_vertex_recovery,ttl):
    temp=[]
    for zone in old_vertex_recovery:
        t = str(ttl[old_vertex_recovery.index(zone)]).split(' ')[0].split('-')

        cloc= str(datetime.now() - datetime(int(t[0]), int(t[1]), int(t[2]))).split(' ')[0]
        if cloc > '0' or cloc.find(':'):
            if vertify.zone_min_size(old_vertex_recovery)[0] != 1: break
            temp.append(old_vertex_recovery.index(zone))
            #del ttl[old_vertex_recovery.index(zone)]
            #old_vertex_recovery.remove(zone)

    temp.sort(reverse = True)  #뒤에 index 부터 지우게
    if len(temp) != 0:
        connectDB.delete_ttl(cache_uid, temp)
        #connectDB.delete_DB_old_vertex_recovery(cache_uid, temp) => 자동으로 관련된 old_vertex_recovery cascade로 지워지넹

    max_x = 0; max_y = 0; min_x = 200; min_y = 200
    for vertex in old_vertex_recovery:
        if (vertex[0][0] > max_x): max_x = vertex[0][0]  # 좌표순서는 1(좌측최상단) 2 3 4(좌측최하단)
        if (vertex[0][1] < min_y): min_y = vertex[0][1]

    return max_x, min_y, old_vertex_recovery, ttl



def start_perbox_newver(old_vertex,old_vertex_recovery,per_box_size,ttl):
    total_min_x, total_min_y, total_max_x, total_max_y, coordi_sort1 = find_minmax_vertex(old_vertex)
    temp_x = total_max_x  # frontemd에서 좌표 받아오면 전체 safe_zone에 대한 꼭지점임. 개개인 박스 꼭짓점이 아니고!!
    temp_y = total_min_y  # 내가 personal_box 사이즈로 나눠서 어짜피 좌표 다 하나씩 일일히 추가해야함
    per_box = per_box_size / 100000
    digit = len(str(per_box)) - 2
    t_x = temp_x
    while True:
        t_y = temp_y
        if (t_x <= total_min_x): break  # 이 말은 다음 경우 포함. x=-10인데, 박스 만들라보니까 마지막 박스가x=-9~-12로 됨. 즉 -10인 원래 경계는 오바했으나, 박스 하나 추가되면서 끝나는거므로 ㅇ
        while True:  # 이 말은 다음 경우 포함. y=10인데, 박스 만들라보니까 마지막 박스가y=9~12로 됨. 즉 10인 원래 경계는 오바했으나, 박스 하나 추가되면서 끝나는거므로 ㅇㅋ
            if (t_y >= total_max_y): break
            temp = []
            t_xx = round(t_x,digit);t_yy = round(t_y,digit);t_xx_per = round(t_x - per_box,digit);t_yy_per = round(t_y + per_box,digit)
            temp.append((t_yy,t_xx))
            temp.append((t_yy_per, t_xx))
            temp.append((t_yy_per, t_xx_per))
            temp.append((t_yy, t_xx_per))
            temp.append((t_yy, t_xx))
            ttl.append(0)#temp.append(0) #old_vertex에 포함되어있지 않다는 소리!!!!
            old_vertex_recovery.append(temp)
            t_y = t_y + per_box

        t_x = t_x - per_box

    return temp_x, temp_y, old_vertex_recovery,ttl #좌표 4개씩으로 된거만 추가되어있고, 시간ttl은 없다!!