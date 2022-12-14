from django.urls import path, re_path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    #path('', views.shelter_list, name='shelter_list'),
    #path('shelter/<int:pk>', views.shelter_detail, name='shelter_detail'),

    # Authentication
    path('login/', views.login_view, name="login"), 
    path('login', views.login_view, name="login"),

    path('register/', views.register_user, name="register"), 
    path('register', views.register_user, name="register"),

    path("logout/", views.logout_view, name="logout"), 
    path("logout", views.logout_view, name="logout"),

    path('', views.index, name='home'),
    #path('chart/<int:sensorId>/', views.chart_view, name="chart"), path('chart/<int:sensorId>', views.chart_view, name="chart"),
    path('line-graph/<int:sensorId>/<str:startDate>/<str:startTime>/<str:endDate>/<str:endTime>', views.fetch_lineChartData, name='line-graph'), 
    path('line-graph/<int:sensorId>/<str:startDate>/<str:startTime>/<str:endDate>/<str:endTime>/', views.fetch_lineChartData, name='line-graph'),

    path('fetchLocations', views.fetch_locations, name='locationData'), 
    path('fetchLocations/', views.fetch_locations, name='locationData'),

    path("tables/", views.table_view, name="tables"), 
    path("tables", views.table_view, name="tables"), 

    path("profile/", views.profile_view, name="profile"), 
    path("profile", views.profile_view, name="profile"),

    re_path(r'^.*\.*', views.pages, name='pages'),

]
