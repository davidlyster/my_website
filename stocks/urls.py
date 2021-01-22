from django.urls import path
from stocks import views

urlpatterns = [
    # the views.xx correspond to functions in views.py
    path('', views.stocks_main, name='stocks'),
]
