from django.urls import path
from . import views 

urlpatterns = [
    path('', views.index, name='home'),
    path('hub/', views.hub, name='hub'),
    path('profile/', views.profile, name='profile'),  # Добавьте этот путь
]