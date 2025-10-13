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
    path('applications/', views.applications_list, name='applications_list'),
    path('applications/<int:application_id>/update-status/', views.update_application_status, name='update_application_status'),
    path('<int:pk>', views.NewDetailView.as_view(), name='application_detail' ),
]