from django.shortcuts import render
from dev_config import TESTING
import os
from django.conf import settings
from django.http import HttpResponse, Http404


def search_main(request):

    context = {}

    # xyxy updated once page is made
    if TESTING:
        return render(request, 'searcher_testing.html', context)
    else:
        return render(request, 'searcher_main.html', context)
