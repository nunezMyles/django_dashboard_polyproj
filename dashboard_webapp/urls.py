from django.urls import path, re_path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    #path('', views.shelter_list, name='shelter_list'),
    #path('shelter/<int:pk>', views.shelter_detail, name='shelter_detail'),

    # Authentication
    path('login/', views.login_view, name="login"),
    path('register/', views.register_user, name="register"),
    path("logout/", views.logout_view, name="logout"),

    path('', views.index, name='home'),
    path('line-graph/', views.line_graph, name='line-graph'),
    path("tables/", views.table_view, name="tables"),
    path("profile/", views.profile_view, name="profile"),

    re_path(r'^.*\.*', views.pages, name='pages'),

]
