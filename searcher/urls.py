from django.urls import path
from searcher import views

urlpatterns = [
    # the views.xx correspond to functions in views.py
    path('', views.search_main, name='searcher'),
]
