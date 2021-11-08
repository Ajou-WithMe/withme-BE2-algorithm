import constants,connectDB,vertify,util
from .models import SafeZone, User, ZoneLocation,UserOption,Location, InitSafeZone

def update_safe_zone():
    # 먼저 최소 size 검증을 진행하기 위해서 all_vertex를 DB에서 load
    a = UserOption.objects.filter(is_init_safe_zone__lt = 1)
    print(len(a))
    for i in range(len(a)):
        if a[i].is_init_safe_zone != 0: continue
        print(a[i].user_id);all_vertex = []
        all_vertex, constants.per_box_size, constants.sum_dist, constants.count_t = connectDB.load_DB_all_vertex(a[i].user_id)  # 8만개 data 효택 DB에서 load, 평균속도도 load
        constants.per_box_size = 100
        #constants.per_box_size = (constants.sum_dist / constants.count_t) * 90
        stat, total_max_x, total_min_y = vertify.zone_min_size(all_vertex)
        '''
        if stat != 1:
            print('safe_zone을 그릴 수 있는 최소 size를 충족하지 않습니다.')
            # connectDB.save_DB_old_vertex_recovery_one(cache_uid, ('X','X'))
            continue
        '''

        if stat != 1:continue
        constants.old_vertex_recovery = []; constants.ttl=[]
        constants.start_section = 1  # 8일이라고 8일에 갑자기 100회 이거 진행하는거 아니자나. 8일되었을때라도 딱 한번만 진행되어야하자나
        constants.temp_x, constants.temp_y, constants.old_vertex_recovery, constants.ttl = util.personal_box_first_time(constants.old_vertex_recovery, all_vertex,constants.per_box_size, constants.ttl, a[i].user_id)
        connectDB.delete_all_recovery_ttl(a[i].user_id)
        connectDB.delete_all_old_vertex_recovery(a[i].user_id)
        connectDB.save_recovery_ttl(a[i].user_id, constants.ttl)
        connectDB.save_DB_old_vertex_recovery(a[i].user_id, constants.old_vertex_recovery)
        connectDB.save_variable_DB(a[i].user_id, constants.per_box_size, constants.sum_dist, constants.count_t, constants.temp_x, constants.temp_y, constants.start_section)


def delete_expire_ttl():
    a = UserOption.objects.all()
    print(len(a))
    for i in range(len(a)):
        if a[i].is_init_safe_zone != 1: continue
        constants.ttl = connectDB.load_recovery_ttl(a[i].user_id)
        constants.old_vertex_recovery = connectDB.load_DB_old_vertex_recovery(a[i].user_id)
        constants.temp_x, constants.temp_y, constants.old_vertex_recovery, constants.ttl = util.personal_box_recovery_all_users(a[i].user_id, constants.old_vertex_recovery, constants.ttl)
        connectDB.save_variable_DB(a[i].user_id, a[i].box_size, a[i].distance, a[i].time, constants.temp_x, constants.temp_y, a[i].is_init_safe_zone)
        #frontend에서는, 어차피 낮에 활동할때 바뀐 safe_zone에 대해서 내부외부 검증하고, 외부면 safe_zone 가져와서 그리므로, 따로 signal 안 보내줘도 괜찮음

