# -*- encoding: utf-8 -*-

from django.urls import path, re_path, include
from app import views
from django.views.generic.base import TemplateView


urlpatterns = [
    # Matches any html file 
    # re_path(r'^.*', views.pages, name='pages'),

    # The home page
    path('', views.index, name='home'),

    # add in project paths
    path('twitterapp/', include('twitterapp.urls')),
    path('stocks/', include('stocks.urls')),
    path('searcher/', include('searcher.urls')),
    path('resume/', views.cv_page, name='Resume'),
]
