from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('get-github-catlogs', views.get_github_json, name='fetch_github_json'),
    
    ]
