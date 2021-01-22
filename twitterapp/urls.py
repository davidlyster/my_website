from django.urls import path
from twitterapp import views

urlpatterns = [
    # the views.xx correspond to functions in views.py
    path('', views.twitter_main, name='twitterapp'),
]
