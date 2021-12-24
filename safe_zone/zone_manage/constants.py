"""
made by BaekJongSeong
notice: do not use global constants
warning: if we use global for this project, Conflicts happen almost at any moment
"""


global count_t
count_t = 0 #3초가 몇번 지났는지
global TIME_INTVL
TIME_INTVL = 5 #시간 주기 5초
global status
status=0 #new_data 검증 결과
global sum_dist
sum_dist =0 #누적거리(평균속도 계산용)
global prev_data
prev_data = tuple([0,0]) #누적거리 계산 위해서 이전 좌표 기록
global new_data
new_data = tuple()
global old_vertex
old_vertex=[] #꼭짓점(용진이가 준 safe_zone 전체에 대한)
global old_vertex_recovery
old_vertex_recovery=[]  #내가 만든 personal_box에 대한 꼭짓점모음
global new_uid
new_uid=-1
global cache_uid
cache_uid=0 #캐싱된 user_id ==new_uid 확인 위한 변수
global temp_x, temp_y
temp_x=0; temp_y=0
global per_box_size
per_box_size = 100.0
global zone_mature_time
zone_mature_time =0
global start_section
start_section=0
global all_vertex
global user_ip
global user_ttl
user_ttl='0'
global ttl
ttl=[]
