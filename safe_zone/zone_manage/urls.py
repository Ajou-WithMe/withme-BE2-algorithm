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
    path('c/',views.connect, name = 'connectDB'),
    path('certify_zone/',views.Init_SafeZone, name = 'certify_zone'),
    path('certify_gps/',views.location_test, name = 'certify_gps'),
    #path('certify_zone/<str:uid>/',views.Init_SafeZone, name = 'certify_zone'),
    #path('certify_gps/<str:uid>/',views.location_test, name = 'certify_gps'),
]
