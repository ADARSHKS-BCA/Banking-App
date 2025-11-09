from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    path('deposit/', views.deposit, name='deposit'),
    path('withdraw/', views.withdraw, name='withdraw'),
    path('transfer/', views.transfer, name='transfer'),
    path('history/<str:account_number>/', views.transaction_history, name='transaction_history'),
    path('all/', views.all_transactions, name='all_transactions'),
]

