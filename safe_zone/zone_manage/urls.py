"""zone_manage URL Configuration
made by BaekJongSeong
All configuration(django) is here in urls.py
in the future, do not use / in last address part
"""
from django.urls import path
from . import views
urlpatterns = [
    #8000 server (which running for each 5 second)
    path('certify_zone/',views.Init_SafeZone, name = 'certify_zone'),
    path('certify_gps/',views.location_test, name = 'certify_gps'),
    #8040 server
    path('certify_put/',views.put, name = 'certify_put'),
    path('certify/<str:uid>/',views.test_for_location, name = 'certify'),
    path('certify_1/',views.update_safe_zone, name = 'certify_1'),
    path('certify_2/',views.delete_expire_ttl, name = 'certify_2'),
    path('certify_often/<int:id>/', views.visit_often, name='certify_often'),
    path('certify_often_put/<int:id>/', views.visit_often_put, name='certify_often_put'),
    path('certify_for/', views.for_predict_test, name='certify_for'),
    path('certify_user/', views.check_user, name='certify_user'),
    path('certify_create/<int:id>/', views.create_check, name='certify_create'),
    path('certify_make_model/<int:id>/', views.make_model, name='certify_make_model'),
    path('certify_predict/<int:id>/', views.search_for_prediction, name='certify_predict'),
    path('test/', views.test,name='test')
    #path('c/',views.connect, name = 'connectDB'),
    #path('certify_zone/<str:uid>/',views.Init_SafeZone, name = 'certify_zone'),
    #path('certify_gps/<str:uid>/',views.location_test, name = 'certify_gps'),
]
