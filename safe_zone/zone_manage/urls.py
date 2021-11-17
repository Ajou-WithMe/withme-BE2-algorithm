"""con_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views
urlpatterns = [
    path('certify_zone/',views.Init_SafeZone, name = 'certify_zone'),
    path('certify_put/',views.put, name = 'certify_put'),
    path('certify_gps/',views.location_test, name = 'certify_gps'),
    path('certify/',views.test_for_location, name = 'certify'),
    path('certify_1/',views.con_test11, name = 'certify_1'),
    path('certify_2/',views.con_test22, name = 'certify_2'),
    path('test/', views.test, name='test'),
    path('certify_often/<int:id>/', views.visit_often, name='certify_often'),
    path('certify_often_put/<int:id>/', views.visit_often_put, name='certify_often_put'),
    path('certify_for/', views.for_predict_test, name='certify_for'),
    path('certify_user/', views.check_user, name='certify_user'),
    path('certify_create/<int:id>/', views.create_check, name='certify_create'),
    #path('c/',views.connect, name = 'connectDB'),
    #path('certify_zone/<str:uid>/',views.Init_SafeZone, name = 'certify_zone'),
    #path('certify_gps/<str:uid>/',views.location_test, name = 'certify_gps'),
]
