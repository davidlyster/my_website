# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse
from django import template
from dev_config import TESTING

# @login_required(login_url="/login/")
def index(request):
    if TESTING:
        return render(request, "index.html")
    else:
        return render(request, "homepage.html")


# @login_required(login_url="/login/")
def cv_page(request):
    return render(request, "cv_page.html")
