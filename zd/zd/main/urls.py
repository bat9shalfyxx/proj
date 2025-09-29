from django.urls import path
from . import views 
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.index, name='home'),
    path('validate-email/', views.validate_email, name='validate_email'),
    path('validate-phone/', views.validate_phone, name='validate_phone'),
    path('hub/', views.hub, name='hub'),
    path('profile/', views.profile, name='profile'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
]