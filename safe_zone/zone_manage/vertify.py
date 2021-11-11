from datetime import datetime, timedelta
from . import util, connectDB
from django.utils import timezone
#from con_project.project import connectDB
import re,pytz

def list_chunk(lst, n):
    return [tuple(lst[i:i+n]) for i in range(0, len(lst), n)]


def data_split1(msg):
    tem = msg.split('|')
    tem2 = tem[0].split(',')
    a = float(tem2[0].split('(')[1])
    b = float(tem2[1].split(')')[0])
    return tuple((a, b)), tem[1]


def data_split2(msg):
    tem = msg.split('[')[1].split(']')
    new_uid = tem[1].split('|')[1]
    a = re.sub('[(]', '', tem[0])
    a = re.sub('[)]', '', a)
    b = a.split('|')
    c= list(map(float,b))
    old_vertex = list_chunk(c, 2)

    return old_vertex,new_uid


def zone_min_size(old_vertex):
    #4.23KM
    total_min_x, total_min_y, total_max_x, total_max_y, coordi_sort1 = util.find_minmax_vertex(old_vertex)
    if abs(total_max_x - total_min_x) < 0.0423:
        stat=3
        if abs(total_max_y-total_min_y) < 0.0423: stat=4
    elif abs(total_max_y - total_min_y) < 0.0423:
        stat=2
        if abs(total_max_x-total_min_x) < 0.0423: stat=4
    else:
        stat=1
    return stat, total_max_x, total_min_y


def check_data_special(old_vertex, old_vertex_recovery,ttl): # 경계선에 걸쳐도 외부로 감지합니다
    per=[]
    #old_vertex.reverse()
    for old in old_vertex_recovery:
        status = 0
        for new_data in old:
            count = 0
            for curr in range(0, len(old_vertex)):
                #if (curr == len(old)-1):
                #    prev = old[curr]
                #    next = old[0]
                #else:
                prev = old_vertex[curr - 1]
                next = old_vertex[curr]

                if ((next[1] < new_data[1] and prev[1] >= new_data[1]) or (prev[1] < new_data[1] and next[1] >= new_data[1])):
                    if (next[0]+(new_data[1]-next[1]) / (prev[1]-next[1]) * (prev[0]-next[0]) < new_data[0]):
                        status = 1
                        count += 1

            #if count % 2 == 0: status = 2
            if status != 1 or count % 2 == 0:  status = 2
            if status == 1: break

        if status == 2: per.append(old)

    for p in per:
        ttl.remove(ttl[old_vertex_recovery.index(p)])
        old_vertex_recovery.remove(p)

    return old_vertex_recovery, ttl


def check_data_sub(new_data, old_vertex,status): # 경계선에 걸쳐도 외부로 감지합니다
    old=old_vertex[:]
    old.reverse()

    count = 0
    for curr in range(1, len(old)):
        #if (curr == len(old)-1):
        #    prev = old[curr]
        #    next = old[0]
        #else:
        prev = old[curr - 1]
        next = old[curr]

        if ((next[1] < new_data[1] and prev[1] >= new_data[1]) or (prev[1] < new_data[1] and next[1] >= new_data[1])):
            if (next[0]+(new_data[1]-next[1]) / (prev[1]-next[1]) * (prev[0]-next[0]) < new_data[0]):
                status = 1
                count += 1

    if count % 2 == 0: status = 2
    if status != 1:  status = 2
    return status


def check_data_sub2(new_data, old_vertex_recovery, status_sub):
    for old_vertex in old_vertex_recovery:
        count = 0
        for curr in range(4):#3 #range(1, 4):  # for curr in range(1,len(old_vertex)):
            #if (curr % 4 == 0):#(curr % 4 == 3):  # if (curr == len(old_vertex)):
            #    prev = old_vertex[curr]  # curr -1
            #    next = old_vertex[curr + 3]#[curr - 3]
            #else:
            prev = old_vertex[curr-1]#[curr]
            next = old_vertex[curr]#[curr-1]

            if ((next[1] < new_data[1] and prev[1] >= new_data[1]) or (prev[1] < new_data[1] and next[1] >= new_data[1])):
                if (next[0] + (new_data[1] - next[1]) / (prev[1] - next[1]) * (prev[0] - next[0]) < new_data[0]):
                    status_sub = 1
                    count += 1
        #if count % 2 == 0: status_sub = 2
        if status_sub == 1:
            return status_sub, old_vertex
        if (status_sub != 1): status_sub = 2
    return status_sub, 0


def check_data_main(new_data, old_vertex_recovery, status,ttl_temp, cache_uid):
    flag=0
    if str(type(ttl_temp)).find('QuerySet') > 0: flag=1
    else: flag=2

    for old_vertex in old_vertex_recovery:
        count = 0
        for curr in range(4):  # for curr in range(1,len(old_vertex)):
            #if len(old_vertex[curr]) != 2: continue
            #if (curr % 5 == 3):  # if (curr == len(old_vertex)):
            #    prev = old_vertex[curr]  # curr -1
            #    next = old_vertex[curr - 3]
            #else:
            prev = old_vertex[curr - 1]  # [curr]
            next = old_vertex[curr]  # [curr-1]

            if ((next[1] < new_data[1] and prev[1] >= new_data[1]) or (prev[1] < new_data[1] and next[1] >= new_data[1])):
                if (next[0] + (new_data[1] - next[1]) / (prev[1] - next[1]) * (prev[0] - next[0]) < new_data[0]):
                    status = 1
                    count += 1
        #if count % 2 == 0: status = 2
        if status == 1:
            if flag==2:
                #ttl_temp = util.ttl_update(ttl_temp)
                return status
                #connectDB.save_recovery_ttl_mod(cache_uid, value, ttl_temp)
            elif flag==1:
                #ttl_temp[old_vertex_recovery.index(old_vertex)]
                t= util.ttl_update(ttl_temp[old_vertex_recovery.index(old_vertex)])
                connectDB.save_recovery_ttl_mod(cache_uid, t, old_vertex_recovery.index(old_vertex))
                return status,ttl_temp
        if (status != 1): status = 2;continue
    return status,ttl_temp


def start_perbox_add(old_vertex_new,new_data,temp_x,temp_y,per_box_size,ttl_temp):
    per_box = per_box_size / 100000
    digit = len(str(per_box)) - 2
    local_tz = pytz.timezone("Asia/Seoul")
    converted_utc_dt = datetime.now() + timedelta(days=1)
    ttl_temp = pytz.utc.localize(converted_utc_dt).astimezone(local_tz)
    if temp_x < new_data[0]:
        t_x = temp_x
        while True:
            t_x = t_x + per_box
            if (t_x > new_data[0]): break

        if temp_y > new_data[1]:
            t_y = temp_y
            while True:
                t_y = t_y - per_box
                if (t_y < new_data[1]): break
            t_xx = round(t_x, digit); t_yy = round(t_y, digit);t_xx_per = round(t_x - per_box, digit);t_yy_per = round(t_y + per_box, digit)
            temp = []
            temp.append((t_xx, t_yy))
            temp.append((t_xx, t_yy_per))
            temp.append((t_xx_per, t_yy_per))
            temp.append((t_xx_per, t_yy))
            #ttl_temp = timezone.now().astimezone() + timedelta(days=1)
            #old_vertex_recovery.append(temp)
            old_vertex_new = temp

        else:
            t_y = temp_y
            while True:
                if (t_y + per_box > new_data[1]):break
                t_y = t_y + per_box
            t_xx = round(t_x, digit); t_yy = round(t_y, digit);t_xx_per = round(t_x - per_box, digit);t_yy_per = round(t_y + per_box, digit)
            temp = []
            temp.append((t_xx, t_yy))
            temp.append((t_xx, t_yy_per))
            temp.append((t_xx_per, t_yy_per))
            temp.append((t_xx_per, t_yy))
            #ttl_temp = timezone.now().astimezone() + timedelta(days=1)
            #old_vertex_recovery.append(temp)
            old_vertex_new = temp

    else:
        t_x = temp_x
        while True:
            if (t_x - per_box < new_data[0]): break
            t_x = t_x - per_box

        if temp_y > new_data[1]:
            t_y = temp_y
            while True:
                t_y = t_y - per_box
                if (t_y < new_data[1]): break
            t_xx = round(t_x, digit); t_yy = round(t_y, digit);t_xx_per = round(t_x - per_box, digit);t_yy_per = round(t_y + per_box, digit)
            temp = []
            temp.append((t_xx, t_yy))
            temp.append((t_xx, t_yy_per))
            temp.append((t_xx_per, t_yy_per))
            temp.append((t_xx_per, t_yy))
            #ttl_temp = timezone.now().astimezone() + timedelta(days=1)
            #old_vertex_recovery.append(temp)
            old_vertex_new = temp

        else:
            t_y = temp_y
            while True:
                if (t_y + per_box > new_data[1]): break
                t_y = t_y + per_box
            t_xx = round(t_x, digit); t_yy = round(t_y, digit);t_xx_per = round(t_x - per_box, digit);t_yy_per = round(t_y + per_box, digit)
            temp = []
            temp.append((t_xx, t_yy))
            temp.append((t_xx, t_yy_per))
            temp.append((t_xx_per, t_yy_per))
            temp.append((t_xx_per, t_yy))
            #ttl_temp = timezone.now().astimezone() + timedelta(days=1)
            #old_vertex_recovery.append(temp)
            old_vertex_new = temp
    return old_vertex_new, ttl_temp


def safe_zone_process(old_vertex_new,new_data,temp_x,temp_y,per_box_size,ttl_temp):
    local_tz = pytz.timezone("Asia/Seoul")
    converted_utc_dt = datetime.now() + timedelta(days=1)
    ttl_temp = pytz.utc.localize(converted_utc_dt).astimezone(local_tz)
    per_box = per_box_size / 100000
    digit = len(str(per_box)) - 2

    if temp_x < new_data[0]:
        t_x = temp_x
        while True:
            t_x = t_x + per_box
            if (t_x > new_data[0]): break

        if temp_y > new_data[1]:
            t_y = temp_y
            while True:
                t_y = t_y - per_box
                if (t_y < new_data[1]): break
            t_xx = round(t_x, digit); t_yy = round(t_y, digit);t_xx_per = round(t_x - per_box, digit);t_yy_per = round(t_y + per_box, digit)
            temp = []
            temp.append((t_xx, t_yy))
            temp.append((t_xx, t_yy_per))
            temp.append((t_xx_per, t_yy_per))
            temp.append((t_xx_per, t_yy))
            #ttl_temp=ttl
            #old_vertex_recovery.append(temp)
            old_vertex_new = temp

        else:
            t_y = temp_y
            while True:
                if (t_y + per_box > new_data[1]):break
                t_y = t_y + per_box
            t_xx = round(t_x, digit); t_yy = round(t_y, digit);t_xx_per = round(t_x - per_box, digit);t_yy_per = round(t_y + per_box, digit)
            temp = []
            temp.append((t_xx, t_yy))
            temp.append((t_xx, t_yy_per))
            temp.append((t_xx_per, t_yy_per))
            temp.append((t_xx_per, t_yy))
            #ttl_temp=ttl
            #old_vertex_recovery.append(temp)
            old_vertex_new = temp


    else:
        t_x = temp_x
        while True:
            if (t_x - per_box < new_data[0]): break
            t_x = t_x - per_box

        if temp_y > new_data[1]:
            t_y = temp_y
            while True:
                t_y = t_y - per_box
                if (t_y < new_data[1]): break
            t_xx = round(t_x, digit);t_yy = round(t_y, digit);t_xx_per = round(t_x - per_box, digit);t_yy_per = round(t_y + per_box, digit)
            temp = []
            temp.append((t_xx, t_yy))
            temp.append((t_xx, t_yy_per))
            temp.append((t_xx_per, t_yy_per))
            temp.append((t_xx_per, t_yy))
            #ttl_temp=ttl
            #old_vertex_recovery.append(temp)
            old_vertex_new = temp

        else:
            t_y = temp_y
            while True:
                if (t_y + per_box > new_data[1]): break
                t_y = t_y + per_box
            t_xx = round(t_x, digit); t_yy = round(t_y, digit);t_xx_per = round(t_x - per_box, digit);t_yy_per = round(t_y + per_box, digit)
            temp = []
            temp.append((t_xx, t_yy))
            temp.append((t_xx, t_yy_per))
            temp.append((t_xx_per, t_yy_per))
            temp.append((t_xx_per, t_yy))
            #ttl_temp=ttl
            #old_vertex_recovery.append(temp)
            old_vertex_new = temp

    return old_vertex_new,ttl_temp


def start_perbox_add_newvr(old_vertex_new,t,temp_x, temp_y,per_box_size, ttl_temp):
    per_box = per_box_size / 100000
    digit = len(str(per_box)) - 2

    if temp_x < t[0]:
        t_x = temp_x
        while True:
            t_x = t_x + per_box
            if (t_x > t[0]): break

        if temp_y > t[1]:
            t_y = temp_y
            while True:
                t_y = t_y - per_box
                if (t_y < t[1]): break
            t_xx = round(t_x, digit); t_yy = round(t_y, digit);t_xx_per = round(t_x - per_box, digit);t_yy_per = round(t_y - per_box, digit)
            temp = []
            temp.append((t_yy_per, t_xx))
            temp.append((t_yy, t_xx))
            temp.append((t_yy, t_xx_per))
            temp.append((t_yy_per, t_xx_per))
            temp.append((t_yy_per, t_xx))
            ttl_temp=1
            old_vertex_new = temp

        else:
            t_y = temp_y
            while True:
                if (t_y + per_box > t[1]):break
                t_y = t_y + per_box
            t_xx = round(t_x, digit); t_yy = round(t_y, digit);t_xx_per = round(t_x - per_box, digit);t_yy_per = round(t_y + per_box, digit)
            temp = []
            temp.append((t_yy, t_xx))
            temp.append((t_yy_per, t_xx))
            temp.append((t_yy_per, t_xx_per))
            temp.append((t_yy, t_xx_per))
            temp.append((t_yy, t_xx))
            ttl_temp=1
            old_vertex_new = temp

    else:
        t_x = temp_x
        while True:
            if (t_x - per_box > t[0]): break
            t_x = t_x - per_box

        if temp_y > t[1]:
            t_y = temp_y
            while True:
                t_y = t_y - per_box
                if (t_y < t[1]): break
            t_xx = round(t_x, digit); t_yy = round(t_y, digit);t_xx_per = round(t_x - per_box, digit);t_yy_per = round(t_y - per_box, digit)
            temp = []
            temp.append((t_yy_per, t_xx))
            temp.append((t_yy, t_xx))
            temp.append((t_yy, t_xx_per))
            temp.append((t_yy_per, t_xx_per))
            temp.append((t_yy_per, t_xx))
            ttl_temp=1
            old_vertex_new = temp

        else:
            t_y = temp_y
            while True:
                if (t_y + per_box > t[1]): break
                t_y = t_y + per_box
            t_xx = round(t_x, digit); t_yy = round(t_y, digit);t_xx_per = round(t_x - per_box, digit);t_yy_per = round(t_y + per_box, digit)
            temp = []
            temp.append((t_yy, t_xx))
            temp.append((t_yy_per, t_xx))
            temp.append((t_yy_per, t_xx_per))
            temp.append((t_yy, t_xx_per))
            temp.append((t_yy, t_xx))
            ttl_temp=1
            old_vertex_new = temp

    return old_vertex_new, ttl_temp
