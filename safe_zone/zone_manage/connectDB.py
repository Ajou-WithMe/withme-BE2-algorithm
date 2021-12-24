"""
made by BaekJongSeong
here for connection with database (AWS RDS)

we connect mysql for this project
django & spring framework both of them access mysql, and modify each part
all CRUD have to access User table to get user_id or uid.
=> every def function start with this code.
some CRUD is replaced for performance inhencement
"""


import sqlite3, io, os, copy
#import django
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "safe_zone.settings")
#django.setup()
from .models import SafeZone, User, ZoneLocation,UserOption,Location, InitSafeZone

#for testing
def con_nect():
    User.objects.filter(id=1)
    return


#just insert init_safe_zone_for_first_time: InitSafeZone Table
def save_DB_old_vertex(new_uid,old_vertex):
    temp = User.objects.get(uid = new_uid)
    temp_t=[]
    for old in old_vertex:
        t = InitSafeZone(latitude=old[0], longitude=old[1], user_id= temp.id)
        temp_t.append(t)
    InitSafeZone.objects.bulk_create(temp_t) #for performance inhencement
    return


#init_safe_zone table: very big size (just one segment (whole)) for first time.
# we just slice them into very tiny boxes for management safe_zone. this part for manage our safe_zone in TTL(data policy)
def save_recovery_ttl(new_uid,ttl):
    temp = User.objects.get(uid=new_uid)
    temp_t = []
    for old in ttl:
        t = SafeZone(ttl = old, user_id= temp.id)
        temp_t.append(t)
    SafeZone.objects.bulk_create(temp_t, batch_size=999) #for performance inhencement
    return


#init_safe_zone is very big size for first time.
# we just slice them into very tiny boxes for management safe_zone. this part for manage our safe_zone perbox
#this old_vertex_recovery is not same with old_vertex.
# first one is dummy of perboxes. second one is first one when user draw safe_zone(initally)
def save_DB_old_vertex_recovery(new_uid,old_vertex_recovery):
    te = User.objects.get(uid=new_uid)
    # load all safe_zone_id for just one user_id
    temp = SafeZone.objects.filter(user_id=te.id).values_list('id',flat=True)
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


# point: we save useroption table before using this function
# so we just modify data and resave it
def save_user_ttl(new_uid, user_ttl,x_temp,y_temp):
    temp = User.objects.get(uid=new_uid)
    t = UserOption.objects.get(user_id=temp.id)
    t.box_size, t.is_init_safe_zone, t.x_temp, t.y_temp = 100.0, 0, x_temp, y_temp
    t.save()
    return


def save_variable_DB(cache_uid,per_box_size, sum_dist, count_t,temp_x, temp_y, start_section):
    temp = User.objects.get(uid=cache_uid)
    t = UserOption.objects.get(user_id=temp.id)
    t.box_size, t.is_init_safe_zone, t.x_temp, t.y_temp= per_box_size,start_section,temp_x,temp_y
    t.save()
    return


def load_recovery_ttl(cache_uid):
    temp = User.objects.get(uid=cache_uid)
    t = SafeZone.objects.filter(user_id=temp.id).values_list('ttl', flat=True)
    print(len(t))
    return t


# we just slice safe_zone into very tiny boxes for management safe_zone.
#we load all perbox into old_vertex_recovery var
def load_DB_old_vertex_recovery(cache_uid):
    te = User.objects.get(uid=cache_uid)
    latitude = ZoneLocation.objects.filter(user_id=te.id).values_list('latitude', flat=True)
    longitude = ZoneLocation.objects.filter(user_id=te.id).values_list('longitude', flat=True)
    # the latitude and longitude both are list type
    list_t=[]
    ls=[]
    count=0

    print(len(latitude),len(longitude))

    # we have to make 2-dimension list for vertify inside / outside of safe_zone
    for i in range(len(latitude)):
        ls.append(tuple([latitude[i],longitude[i]]))
        count+=1
        # so we add this code(slice it) to make 2-dim list
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


#this part is valuable for expand the scope of our safe_zone.
# we can expand the scope(per_box) just one in a time.
def save_recovery_ttl_one(cache_uid,ttl_temp):
    temp = User.objects.get(uid=cache_uid)
    t = SafeZone(ttl = ttl_temp, user_id=temp.id)
    t.save()
    return


#when expanding the scope, upper one is for ttl, and here for safe_zone perbox
def save_DB_old_vertex_recovery_one(cache_uid,old_vertex_new):
    te = User.objects.get(uid=cache_uid)
    temp = SafeZone.objects.filter(user_id=te.id).values_list('id', flat=True)
    print(len(temp))
    t=[]
    for old in old_vertex_new:
        t.append(ZoneLocation(latitude=old[0], longitude=old[1],user_id=te.id, safe_zone_id=temp[len(temp)-1]))
    ZoneLocation.objects.bulk_create(t)
    return


def load_DB_all_vertex(user_id):
    latitude = Location.objects.filter(user_id=user_id).values_list('latitude', flat=True)
    longitude = Location.objects.filter(user_id=user_id).values_list('longitude', flat=True)
    print(len(latitude),len(longitude))
    ls=[]
    for i in range(len(latitude)):
        ls.append(tuple([latitude[i],longitude[i]]))
    t = UserOption.objects.get(user_id=user_id)
    return ls, t.box_size, t.distance, t.time


def load_DB_all_vertex2(user_id):
    latitude = Location.objects.filter(user_id=user_id).values_list('latitude', flat=True)
    longitude = Location.objects.filter(user_id=user_id).values_list('longitude', flat=True)
    created_at = Location.objects.filter(user_id=user_id).values_list('created_at', flat=True)
    print(len(latitude), len(longitude), len(created_at))
    dict_value = [{"latitude": latitude[i],"longitude":longitude[i]} for i in range(len(latitude))]
    dictionary = {"all_vertex" : dict_value}
    created_at=list(created_at)
    return dictionary, created_at


def load_DB_all_vertex3(user_id):
    latitude = Location.objects.filter(user_id=user_id).values_list('latitude', flat=True)
    longitude = Location.objects.filter(user_id=user_id).values_list('longitude', flat=True)
    print(len(latitude), len(longitude))
    dict_value=2
    if len(latitude) > 3:
        dict_value = [{"latitude": latitude[i], "longitude": longitude[i]} for i in range(len(latitude))]
    dictionary = {"all_vertex" : dict_value}
    return dictionary


def delete_all_recovery_ttl(user_id):
    #temp = User.objects.get(uid=cache_uid)
    temp = SafeZone.objects.filter(user_id=user_id)
    temp.delete()
    print('remain is ', len(temp))
    return


def delete_all_old_vertex_recovery(user_id):
    #te = User.objects.get(uid=cache_uid)
    ZoneLocation.objects.filter(user_id=user_id).delete()#SafeZone.objects.filter(user_id=te.id).prefetch_related('id')
    return


#this part for delete ttl(when ttl expired).
# ttl is cascade for zone_location(perbox).
# so when we remove ttl, perbox which related that ttl_id will remove too
def delete_ttl(user_id, old_vertex_delete):
    #temp = User.objects.get(uid=cache_uid)
    count = 0
    while True:
        t = SafeZone.objects.filter(user_id=user_id)
        print(len(t))
        SafeZone.objects.get(pk=t[old_vertex_delete[count]].id).delete()
        count+=1
        if count == len(old_vertex_delete): break
        #for idx in old_vertex_delete:
        #    count += 1
        #    SafeZone.objects.get(pk=t[idx].id).delete()
        #    old_vertex_delete.remove(idx)
        #    if count == 100: break
        #if len(old_vertex_delete) == 0: break
    #for idx in old_vertex_delete:
    #    t[idx].delete()
    return


#this code will be replaced in cascade. so do not use
def delete_DB_old_vertex_recovery(user_id, old_vertex_delete):
    #temp = User.objects.get(uid=cache_uid)
    t = ZoneLocation.objects.filter(user_id=user_id)
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


