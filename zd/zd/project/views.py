from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import transaction
import json
import os

from .models import (
    Project, ProjectRequirement, ProjectInvitation, 
    ProjectParticipant, ProjectFile, ProjectComment
)
from main.models_application import Application


@login_required
def project_list(request):
    #Список проектов пользователя
    # Проекты, где пользователь создатель
    created_projects = Project.objects.filter(creator=request.user).order_by('-created_at')
    
    # Проекты, где пользователь участник
    participating = ProjectParticipant.objects.filter(
        user=request.user, 
        status='active'
    ).select_related('project')
    participating_projects = [p.project for p in participating]
    
    # Приглашения
    invitations = ProjectInvitation.objects.filter(
        application__user=request.user,
        status='pending'
    ).select_related('project', 'invited_by')
    
    context = {
        'created_projects': created_projects,
        'participating_projects': participating_projects,
        'invitations': invitations,
    }
    return render(request, 'projectsList.html', context)


@login_required
def project_create(request):
    #Создание нового проекта

    if request.method == 'POST':
        try:
            with transaction.atomic():
                keywords = request.POST.get('keywords', '')
                
                project = Project.objects.create(
                    name=request.POST.get('name'),
                    description=request.POST.get('description'),
                    team_activities=request.POST.get('team_activities', ''),
                    work_conditions=request.POST.get('work_conditions', ''),
                    start_date=request.POST.get('start_date') or None,
                    end_date=request.POST.get('end_date') or None,
                    budget=request.POST.get('budget') or None,
                    status='draft',
                    creator=request.user,
                    keywords=keywords
                )
                
                # Обработка требований к участникам
                requirement_names = request.POST.getlist('requirement_name[]')
                requirement_levels = request.POST.getlist('requirement_level[]')
                requirement_counts = request.POST.getlist('requirement_count[]')
                requirement_mandatory = request.POST.getlist('requirement_mandatory[]')
                requirement_prices = request.POST.getlist('requirement_price[]')
                requirement_conditions = request.POST.getlist('requirement_condition[]')
                belbin_roles = request.POST.getlist('belbin_role[]')
                
                for i in range(len(requirement_names)):
                    if requirement_names[i].strip():
                        ProjectRequirement.objects.create(
                            project=project,
                            skill_name=requirement_names[i],
                            level_requirement=requirement_levels[i] if i < len(requirement_levels) else '',
                            people_count=int(requirement_counts[i]) if i < len(requirement_counts) else 1,
                            is_mandatory=(requirement_mandatory[i] == 'on') if i < len(requirement_mandatory) else False,
                            price=requirement_prices[i] if i < len(requirement_prices) and requirement_prices[i] else None,
                            work_condition=requirement_conditions[i] if i < len(requirement_conditions) else '',
                            belbin_role=belbin_roles[i] if i < len(belbin_roles) and belbin_roles[i] else ''
                        )
                
                messages.success(request, f'Проект "{project.name}" успешно создан!')
                
                # AJAX ответ
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'redirect_url': f'/projects/{project.id}/'
                    })
                
                return redirect('project_detail', project_id=project.id)
                
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                })
            messages.error(request, f'Ошибка при создании проекта: {e}')
    
    # GET запрос - показываем форму
    return render(request, 'createProject.html', {
        'title': 'Создание проекта'
    })


@login_required
def project_detail(request, project_id):
    #Dетальная страница проекта
    project = get_object_or_404(Project, id=project_id)
    
    # Проверка доступа
    is_creator = (project.creator == request.user)
    is_participant = ProjectParticipant.objects.filter(
        project=project, 
        user=request.user, 
        status='active'
    ).exists()
    
    if not (is_creator or is_participant):
        return HttpResponseForbidden("У вас нет доступа к этому проекту")
    
    # Требования проекта
    requirements = project.requirements.all()
    
    # Участники
    participants = project.participants.filter(status='active')
    
    # Приглашения
    invitations = project.invitations.all().order_by('-invited_at')
    
    # Комментарии
    comments = project.comments.filter(parent=None).order_by('created_at')
    
    # Файлы
    files = project.files.all().order_by('-uploaded_at')
    
    # Доступные кандидаты (из заявок)
    # Исключаем уже приглашенных и участников
    invited_app_ids = project.invitations.values_list('application_id', flat=True)
    participant_app_ids = project.participants.exclude(application=None).values_list('application_id', flat=True)
    excluded_ids = list(invited_app_ids) + list(participant_app_ids)
    
    available_applications = Application.objects.filter(
        user=request.user  # Только заявки текущего пользователя
    ).exclude(
        id__in=excluded_ids
    ) if is_creator else []
    
    # Для создателя - показываем подходящие заявки под требования
    matching_applications = {}
    if is_creator:
        for req in requirements:
            if req.skill_name:
                matching = Application.objects.filter(
                    skill_list__icontains=req.skill_name
                ).exclude(
                    id__in=excluded_ids
                )[:10]  # Ограничим до 10
                matching_applications[req.id] = matching
    
    context = {
        'project': project,
        'requirements': requirements,
        'participants': participants,
        'invitations': invitations,
        'comments': comments,
        'files': files,
        'available_applications': available_applications,
        'matching_applications': matching_applications,
        'total_requirements_sum': project.get_total_requirements_sum(),
        'is_creator': is_creator,
        'is_participant': is_participant,
    }
    return render(request, 'projects/project_detail.html', context)


@login_required
def project_edit(request, project_id):
    #Редактирование проекта
    project = get_object_or_404(Project, id=project_id, creator=request.user)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Обновляем основные поля
                project.name = request.POST.get('name')
                project.description = request.POST.get('description')
                project.team_activities = request.POST.get('team_activities', '')
                project.work_conditions = request.POST.get('work_conditions', '')
                project.start_date = request.POST.get('start_date') or None
                project.end_date = request.POST.get('end_date') or None
                project.budget = request.POST.get('budget') or None
                project.keywords = request.POST.get('keywords', '') 
                project.save()
                
                # Удаляем старые требования
                project.requirements.all().delete()
                
                # Создаем новые требования
                requirement_names = request.POST.getlist('requirement_name[]')
                requirement_levels = request.POST.getlist('requirement_level[]')
                requirement_counts = request.POST.getlist('requirement_count[]')
                requirement_mandatory = request.POST.getlist('requirement_mandatory[]')
                requirement_prices = request.POST.getlist('requirement_price[]')
                requirement_conditions = request.POST.getlist('requirement_condition[]')
                belbin_roles = request.POST.getlist('belbin_role[]')
                
                for i in range(len(requirement_names)):
                    if requirement_names[i].strip():
                        ProjectRequirement.objects.create(
                            project=project,
                            skill_name=requirement_names[i],
                            level_requirement=requirement_levels[i] if i < len(requirement_levels) else '',
                            people_count=int(requirement_counts[i]) if i < len(requirement_counts) else 1,
                            is_mandatory=(requirement_mandatory[i] == 'on') if i < len(requirement_mandatory) else False,
                            price=requirement_prices[i] if i < len(requirement_prices) and requirement_prices[i] else None,
                            work_condition=requirement_conditions[i] if i < len(requirement_conditions) else '',
                            belbin_role=belbin_roles[i] if i < len(belbin_roles) and belbin_roles[i] else ''
                        )
                
                messages.success(request, 'Проект успешно обновлен!')
                return redirect('project_detail', project_id=project.id)
                
        except Exception as e:
            messages.error(request, f'Ошибка при обновлении: {e}')
    

    context = {
        'project': project,
        'requirements': project.requirements.all(),
    }
    return render(request, 'projects/project_edit.html', context)


@login_required
def project_delete(request, project_id):
    #Удаление проекта
    project = get_object_or_404(Project, id=project_id, creator=request.user)
    
    if request.method == 'POST':
        project_name = project.name
        project.delete()
        messages.success(request, f'Проект "{project_name}" удален')
        return redirect('project_list')
    
    return render(request, 'projects/project_confirm_delete.html', {'project': project})


@login_required
def project_change_status(request, project_id):
    #Изменение статуса проекта
    project = get_object_or_404(Project, id=project_id, creator=request.user)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Project.STATUS_CHOICES):
            project.status = new_status
            project.save()
            messages.success(request, f'Статус проекта изменен на "{project.get_status_display()}"')
    
    return redirect('project_detail', project_id=project.id)


@login_required
def invite_to_project(request, project_id):
    #Приглашение участника в проект
    project = get_object_or_404(Project, id=project_id, creator=request.user)
    
    if request.method == 'POST':
        application_id = request.POST.get('application_id')
        message = request.POST.get('message', '')
        
        try:
            application = Application.objects.get(id=application_id)
            
            # Проверяем, не приглашен ли уже
            existing = ProjectInvitation.objects.filter(
                project=project, 
                application=application
            ).exists()
            
            if existing:
                return JsonResponse({
                    'success': False,
                    'error': 'Этот пользователь уже приглашен'
                })
            
            invitation = ProjectInvitation.objects.create(
                project=project,
                application=application,
                invited_by=request.user,
                message=message
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'invitation_id': invitation.id,
                    'message': 'Приглашение отправлено'
                })
            
            messages.success(request, 'Приглашение отправлено')
            
        except Application.DoesNotExist:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Заявка не найдена'})
            messages.error(request, 'Заявка не найдена')
    
    return redirect('project_detail', project_id=project.id)


@login_required
def respond_to_invitation(request, invitation_id):
    #Ответ на приглашение
    invitation = get_object_or_404(
        ProjectInvitation, 
        id=invitation_id,
        application__user=request.user,
        status='pending'
    )
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'accept':
            invitation.accept()
            messages.success(request, f'Вы присоединились к проекту "{invitation.project.name}"')
        elif action == 'decline':
            invitation.decline()
            messages.success(request, 'Приглашение отклонено')
        
        return redirect('project_list')
    
    context = {
        'invitation': invitation,
    }
    return render(request, 'projects/respond_invitation.html', context)


@login_required
def cancel_invitation(request, invitation_id):
    #Отмена приглашения (только для создателя)
    invitation = get_object_or_404(
        ProjectInvitation, 
        id=invitation_id,
        project__creator=request.user
    )
    
    if request.method == 'POST':
        invitation.cancel()
        messages.success(request, 'Приглашение отменено')
    
    return redirect('project_detail', project_id=invitation.project.id)


@login_required
def remove_participant(request, project_id, participant_id):
    #Удаление участника из проекта
    project = get_object_or_404(Project, id=project_id, creator=request.user)
    participant = get_object_or_404(ProjectParticipant, id=participant_id, project=project)
    
    if request.method == 'POST':
        participant.leave_project()
        messages.success(request, f'{participant.full_name} удален из проекта')
    
    return redirect('project_detail', project_id=project.id)


@login_required
def add_comment(request, project_id):
    #Добавление комментария
    project = get_object_or_404(Project, id=project_id)
    
    # Проверка доступа
    is_creator = (project.creator == request.user)
    is_participant = ProjectParticipant.objects.filter(
        project=project, 
        user=request.user, 
        status='active'
    ).exists()
    
    if not (is_creator or is_participant):
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        text = request.POST.get('text')
        parent_id = request.POST.get('parent_id')
        
        if text:
            comment = ProjectComment.objects.create(
                project=project,
                author=request.user,
                text=text,
                parent_id=parent_id if parent_id else None
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'comment_id': comment.id,
                    'author': str(request.user),
                    'text': text,
                    'created_at': comment.created_at.strftime('%d.%m.%Y %H:%M')
                })
            
            messages.success(request, 'Комментарий добавлен')
    
    return redirect('project_detail', project_id=project.id)


@login_required
def upload_file(request, project_id):
    #Загрузка файла в проект
    project = get_object_or_404(Project, id=project_id)
    
    # Проверка доступа
    is_creator = (project.creator == request.user)
    is_participant = ProjectParticipant.objects.filter(
        project=project, 
        user=request.user, 
        status='active'
    ).exists()
    
    if not (is_creator or is_participant):
        return HttpResponseForbidden()
    
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        
        file_obj = ProjectFile.objects.create(
            project=project,
            uploaded_by=request.user,
            file=uploaded_file,
            filename=uploaded_file.name,
            file_size=uploaded_file.size,
            description=request.POST.get('description', '')
        )
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'file_id': file_obj.id,
                'filename': file_obj.filename,
                'file_size': file_obj.file_size,
                'uploaded_at': file_obj.uploaded_at.strftime('%d.%m.%Y')
            })
        
        messages.success(request, 'Файл загружен')
    
    return redirect('project_detail', project_id=project.id)


@login_required
def delete_file(request, project_id, file_id):
    #Удаление файла
    project = get_object_or_404(Project, id=project_id)
    file_obj = get_object_or_404(ProjectFile, id=file_id, project=project)
    
    if request.user != project.creator and request.user != file_obj.uploaded_by:
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        if file_obj.file:
            if os.path.isfile(file_obj.file.path):
                os.remove(file_obj.file.path)
        
        file_obj.delete()
        messages.success(request, 'Файл удален')
    
    return redirect('project_detail', project_id=project.id)