from django.urls import path
from . import views

urlpatterns = [
    # Главные страницы
    path('', views.hub, name='home'),
    path('hub/', views.hub, name='hub'),
    # заявки
    path('form_page/', views.form_page, name='form_page'),
    path('create_team/', views.create_team, name='create_team'),    
    # Профиль и подстраницы
    path('profile/', views.profile, name='profile'),
    path('profile/applications/', views.profile_applications, name='profile_applications'),
    path('profile/events/', views.profile_events, name='profile_events'),
    path('profile/services/', views.profile_services, name='profile_services'),
    path('profile/education/', views.profile_education, name='profile_education'),
    path('profile/support/', views.profile_support, name='profile_support'),
    # Проекты (все маршруты здесь, без отдельного приложения)
    path('all/', views.all_projects, name='all_projects'),
    path('projects/', views.project_list, name='project_list'),
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('projects/<int:project_id>/edit/', views.project_edit, name='project_edit'),
    path('projects/<int:project_id>/delete/', views.project_delete, name='project_delete'),
    path('projects/<int:project_id>/status/', views.project_change_status, name='project_change_status'),
    path('projects/<int:project_id>/leave/', views.leave_project, name='leave_project'),
    path('api/applications_all/', views.api_applications_all, name='api_applications_all'),
    # Запрос на участие в проекте
    path('api/my-applications/', views.my_applications_api, name='my_applications_api'),
    path('api/projects/<int:project_id>/join-request/', views.send_join_request, name='send_join_request'),
    path('api/projects/<int:project_id>/join-requests/', views.project_join_requests, name='project_join_requests'),
    path('api/join-request/<int:request_id>/respond/', views.respond_join_request, name='respond_join_request'),
    # Приглашения
    path('projects/<int:project_id>/invite/', views.invite_to_project, name='invite_to_project'),
    path('invitation/<int:invitation_id>/cancel/', views.cancel_invitation, name='cancel_invitation'),
    path('invitation/<int:invitation_id>/respond/', views.respond_to_invitation, name='respond_to_invitation'),
    # Уведомления
    path('api/notifications/', views.get_notifications, name='get_notifications'),
    path('api/notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('api/notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
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
    # api кандидатов в проект
    path('api/projects/<int:project_id>/candidates/', views.api_applications_for_project, name='api_project_candidates'),
]