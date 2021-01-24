# -*- encoding: utf-8 -*-

from django.urls import path, re_path, include
from app import views

urlpatterns = [
    # Matches any html file 
    re_path(r'^.*\.html', views.pages, name='pages'),

    # The home page
    path('', views.index, name='home'),

    # add in project paths
    path('twitterapp/', include('twitterapp.urls')),
    path('stocks/', include('stocks.urls')),
]
