"""
made by BaekJongSeong
use FK and PK for a solid erd database structure
"""
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
#Foreign Key란 테이블과 테이블을 연결하기 위해 사용
###불필요한 column의 생성을 줄여 단순 구조 유지 가능!!!

#한 테이블에서 FK는 PK처럼 고유하지 않지
# 자식 테이블이라 하며, Foreign Key 값을 갖고 있는 테이블은 부모 테이블


class Auth(models.Model):
    id = models.BigAutoField(primary_key=True)
    access_token = models.CharField(max_length=255, blank=True, null=True)
    refresh_token = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'auth'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Comment(models.Model):
    id = models.BigAutoField(primary_key=True)
    comment = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    post = models.ForeignKey('Post', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'comment'


class CommentReport(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField(blank=True, null=True)
    msg = models.CharField(max_length=255, blank=True, null=True)
    type = models.IntegerField()
    comment = models.ForeignKey(Comment, models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'comment_report'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class InitSafeZone(models.Model):
    id = models.BigAutoField(primary_key=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        #managed = False
        db_table = 'init_safe_zone'


class Location(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    user = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        #managed = False
        db_table = 'location'


class Party(models.Model):
    id = models.BigAutoField(primary_key=True)
    code = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    profile = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        #managed = False
        db_table = 'party'


class PartyMember(models.Model):
    id = models.BigAutoField(primary_key=True)
    type = models.IntegerField()
    party = models.ForeignKey(Party, models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        #managed = False
        db_table = 'party_member'


class Post(models.Model):
    id = models.BigAutoField(primary_key=True)
    activity_radius = models.CharField(max_length=255, blank=True, null=True)
    contact = models.IntegerField()
    content = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    state = models.IntegerField()
    title = models.CharField(max_length=255, blank=True, null=True)
    #guardian = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    #protection = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        #managed = False
        db_table = 'post'


class PostFile(models.Model):
    id = models.BigAutoField(primary_key=True)
    file = models.CharField(max_length=255, blank=True, null=True)
    post = models.ForeignKey(Post, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        #managed = False
        db_table = 'post_file'


class ProjectLocation(models.Model):
    id = models.BigAutoField(primary_key=True)
    latitude = models.BigIntegerField()
    longitude = models.BigIntegerField()

    class Meta:
        #managed = False
        db_table = 'project_location'


class SafeZone(models.Model):
    id = models.BigAutoField(primary_key=True)
    ttl = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey('User',on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        #managed = False
        db_table = 'safe_zone'


class User(models.Model):
    id = models.BigAutoField(primary_key=True)
    address = models.CharField(max_length=255, blank=True, null=True)#null=True 는 필드의 값이 NULL(정보 없음)로 저장되는 것을 허용
    created_at = models.DateTimeField(blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True) #blank=True 는 필드가 폼(입력 양식)에서 빈 채로 저장되는 것을 허용
    name = models.CharField(max_length=255, blank=True, null=True) #Null : DB와 관련
    phone = models.CharField(max_length=255, blank=True, null=True) #Blank : 유효성과 관련
    profile_img = models.CharField(max_length=255, blank=True, null=True)
    pwd = models.CharField(max_length=255, blank=True, null=True)
    type = models.BigIntegerField(blank=True, null=True)
    uid = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        #managed = False
        db_table = 'user'


class UserOption(models.Model):
    id = models.BigAutoField(primary_key=True)
    box_size = models.FloatField(blank=True, null=True)
    current_network = models.DateTimeField(blank=True, null=True)
    distance = models.FloatField(blank=True, null=True)
    is_init_safe_zone = models.IntegerField()
    push_alarm = models.IntegerField()
    safe_move = models.IntegerField()
    time = models.BigIntegerField(blank=True, null=True)
    x_temp = models.FloatField(blank=True, null=True)
    y_temp = models.FloatField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    is_disconnected = models.IntegerField()

    class Meta:
        #managed = False
        db_table = 'user_option'


class ZoneLocation(models.Model):
    id = models.BigAutoField(primary_key=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    safe_zone = models.ForeignKey(SafeZone, on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        #managed = False
        db_table = 'zone_location'


class PredictionLocation(models.Model):
    id = models.BigAutoField(primary_key=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    user = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        #managed = False
        db_table = 'prediction_location'


class VisitOften(models.Model):
    id = models.BigAutoField(primary_key=True)
    grade = models.IntegerField()
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    user = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        #managed = False
        db_table = 'visit_often'