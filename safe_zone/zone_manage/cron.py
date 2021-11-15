import constants,connectDB,vertify,util
from datetime import datetime, timedelta
from .models import SafeZone, User, ZoneLocation,UserOption,Location, InitSafeZone


def update_safe_zone():
    constants.cache_uid = 0
    print('shceduler update_safe_zone after Day 7')
    # 먼저 최소 size 검증을 진행하기 위해서 all_vertex를 DB에서 load
    a = UserOption.objects.filter(is_init_safe_zone__lt=1)
    print(len(a))

    for i in range(len(a)):
        temp = User.objects.get(id=a[i].user_id)
        uid = temp.uid
        t = str(temp.created_at).split(' ')[0].split('-')
        cloc = str(datetime.now() - datetime(int(t[0]), int(t[1]), int(t[2]))).split(' ')[0]
        if cloc <= '7' or cloc.find(':') != -1: continue

        all_vertex = []
        all_vertex, constants.per_box_size, constants.sum_dist, constants.count_t = connectDB.load_DB_all_vertex(a[i].user_id)  # 8만개 data 효택 DB에서 load, 평균속도도 load
        constants.per_box_size = 100
        # constants.per_box_size = (constants.sum_dist / constants.count_t) * 90
        if len(all_vertex) == 0: continue
        stat, total_max_x, total_min_y = vertify.zone_min_size(all_vertex)

        if stat != 1: continue
        constants.old_vertex_recovery = [];        constants.ttl = []
        constants.start_section = 1  # 8일이라고 8일에 갑자기 100회 이거 진행하는거 아니자나. 8일되었을때라도 딱 한번만 진행되어야하자나
        constants.temp_x, constants.temp_y, constants.old_vertex_recovery, constants.ttl = util.personal_box_first_time(
            constants.old_vertex_recovery, all_vertex, constants.per_box_size, constants.ttl, uid)

        print('user safe_zone update')
        connectDB.delete_all_recovery_ttl(a[i].user_id)
        connectDB.save_recovery_ttl(uid, constants.ttl)
        connectDB.save_DB_old_vertex_recovery(uid, constants.old_vertex_recovery)
        connectDB.save_variable_DB(uid, constants.per_box_size, constants.sum_dist, constants.count_t,
                                   constants.temp_x, constants.temp_y, constants.start_section)


def delete_expire_ttl():
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
        #frontend에서는, 어차피 낮에 활동할때 바뀐 safe_zone에 대해서 내부외부 검증하고, 외부면 safe_zone 가져와서 그리므로, 따로 signal 안 보내줘도 괜찮음

