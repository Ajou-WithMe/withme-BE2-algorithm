import constants,connectDB,vertify,util
from datetime import datetime, timedelta
from .models import SafeZone, User, ZoneLocation,UserOption,Location, InitSafeZone


#this part for schedular(periordically exceed)
def update_safe_zone():
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


def delete_expire_ttl():
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


