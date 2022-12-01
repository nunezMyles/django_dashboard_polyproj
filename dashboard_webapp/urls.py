from django.urls import path
from . import views

urlpatterns = [
    #path('', views.live_app, name='live_app_test'),
    path('', views.shelter_list, name='shelter_list'),
    path('shelter/<int:pk>', views.shelter_detail, name='shelter_detail'),
]
