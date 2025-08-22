from django.shortcuts import render
from django.http import Http404

def custom_404_view(request, exception):
    """Custom 404 error page"""
    return render(request, '404.html', status=404)

def custom_500_view(request):
    """Custom 500 error page"""
    return render(request, '500.html', status=500)

