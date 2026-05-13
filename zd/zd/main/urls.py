from django.urls import path
from . import views

urlpatterns = [
    # Главные страницы
    path('', views.hub, name='home'),
    path('hub/', views.hub, name='hub'),
    # Профиль и заявки
    path('profile/', views.profile, name='profile'),
    path('form_page/', views.form_page, name='form_page'),
    path('create_team/', views.create_team, name='create_team'),
    # Проекты (все маршруты здесь, без отдельного приложения)
    path('all/', views.all_projects, name='all_projects'),
    path('projects/', views.project_list, name='project_list'),
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('projects/<int:project_id>/edit/', views.project_edit, name='project_edit'),
    path('projects/<int:project_id>/delete/', views.project_delete, name='project_delete'),
    path('projects/<int:project_id>/status/', views.project_change_status, name='project_change_status'),
    path('api/applications/', views.api_applications, name='api_applications'),
    # Приглашения
    path('projects/<int:project_id>/invite/', views.invite_to_project, name='invite_to_project'),
    path('invitation/<int:invitation_id>/', views.respond_to_invitation, name='respond_to_invitation'),
    path('invitation/<int:invitation_id>/cancel/', views.cancel_invitation, name='cancel_invitation'),
    # Участники
    path('projects/<int:project_id>/participant/<int:participant_id>/remove/', 
         views.remove_participant, name='remove_participant'),
    # Комментарии и файлы
    path('projects/<int:project_id>/comment/', views.add_comment, name='add_comment'),
    path('projects/<int:project_id>/upload/', views.upload_file, name='upload_file'),
    path('projects/<int:project_id>/file/<int:file_id>/delete/', views.delete_file, name='delete_file'),
    # Аутентификация
    path('logout/', views.logout_view, name='logout'),
    # AJAX валидация
    path('validate-email/', views.validate_email, name='validate_email'),
    path('validate-phone/', views.validate_phone, name='validate_phone'),
    # Поиск
    path('search/', views.global_search, name='global_search'),
    # Edit
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    # api заявок
    path('api/applications/', views.api_applications, name='api_applications'),
]