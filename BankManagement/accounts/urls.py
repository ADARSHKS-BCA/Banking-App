from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.account_create, name='account_create'),
    path('list/', views.account_list, name='account_list'),
    path('login/', views.account_login, name='account_login'),
    path('<str:account_number>/', views.account_detail, name='account_detail'),
]

