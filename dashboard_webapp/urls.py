from django.urls import path, re_path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    #path('', views.shelter_list, name='shelter_list'),
    #path('shelter/<int:pk>', views.shelter_detail, name='shelter_detail'),

    # Authentication
    path('login/', views.login_view, name="login"),
    path('register/', views.register_user, name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),

    # Home
    path('', views.index, name='home'),
    re_path(r'^.*\.*', views.pages, name='pages'),

]
