from django.shortcuts import render
from .generative import run_validation


def index(request):
    stats = run_validation()
    context = {
        'stats': stats,
    }
    return render(request, 'index.html', context)
