from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProfileEditForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import transaction
from django import forms
from django.db import models
import json
import os
import re
import logging

from .forms import CustomUserCreationForm, CustomAuthenticationForm, ApplicationForm, ProjectForm, ProjectRequirementForm
from .models import CustomUser, Application, Project, ProjectRequirement, ProjectInvitation, ProjectParticipant, ProjectFile, ProjectComment

logger = logging.getLogger(__name__)
def index(request):
    
    return render(request, 'index.html', {
        'messages': messages.get_messages(request)
    })

def handle_ajax_request(request):
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST.dict()
    except (json.JSONDecodeError, AttributeError):
        data = request.POST.dict() if hasattr(request, 'POST') else {}
    
    action = data.get('action', '')

    if action == 'login':
        login_form = CustomAuthenticationForm(request, data=data)
        
        if login_form.is_valid():
            user = login_form.get_user()
            
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            return JsonResponse({
                'success': True,
                'redirect_url': '/profile/',
                'message': 'Вход выполнен успешно!'
            })
        else:
            
            errors = {}
            for field, field_errors in login_form.errors.items():
                if field == '__all__':
                    errors['general'] = field_errors
                else:
                    errors[field] = field_errors
            
            return JsonResponse({
                'success': False,
                'errors': errors
            })

    elif action == 'register':
        registration_form = CustomUserCreationForm(data)
        
        if registration_form.is_valid():
            user = registration_form.save()
            
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            return JsonResponse({
                'success': True,
                'redirect_url': '/profile/',
                'message': 'Регистрация прошла успешно!'
            })
        else:
           
            errors = {}
            for field, field_errors in registration_form.errors.items():
                if field == '__all__':
                    errors['general'] = field_errors
                else:
                    errors[field] = field_errors
            
            return JsonResponse({
                'success': False,
                'errors': errors
            })
    
    return JsonResponse({
        'success': False, 
        'error': 'Неизвестное действие'
    })

@csrf_exempt
def validate_email(request):
    """AJAX валидация email"""
    if request.method == 'GET':
        email = request.GET.get('email', '').strip().lower()
        logger.info(f'Validating email: {email}')
        
        if not email:
            return JsonResponse({'valid': False, 'message': 'Email обязателен'})
        
        
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            return JsonResponse({'valid': False, 'message': 'Введите корректный адрес электронной почты'})
        
        exists = CustomUser.objects.filter(email__iexact=email).exists()
        logger.info(f'Email {email} exists: {exists}')
        
        return JsonResponse({
            'valid': not exists,
            'exists': exists,
            'message': 'Этот email уже используется' if exists else 'Email доступен'
        })
    
    return JsonResponse({'valid': False, 'message': 'Недопустимый метод запроса'})

@csrf_exempt
def validate_phone(request):
    """AJAX валидация телефона"""
    if request.method == 'GET':
        phone = request.GET.get('phone', '').strip()
        logger.info(f'Validating phone: {phone}')
        
        if not phone:
            return JsonResponse({'valid': False, 'message': 'Номер телефона обязателен'})
        
      
        phone_digits = re.sub(r'[^\d]', '', phone)
        
        if len(phone_digits) not in [10, 11]:
            return JsonResponse({
                'valid': False, 
                'message': 'Номер телефона должен содержать 10 или 11 цифр'
            })
        
        
        if phone_digits.startswith('7'):
            phone_formatted = '+' + phone_digits
        elif phone_digits.startswith('8'):
            phone_formatted = '+7' + phone_digits[1:]
        else:
            phone_formatted = '+7' + phone_digits
        
       
        if len(phone_formatted) != 12:
            return JsonResponse({
                'valid': False,
                'message': 'Номер телефона должен содержать 11 цифр после +7'
            })
        
        exists = CustomUser.objects.filter(phone_number=phone_formatted).exists()
        logger.info(f'Phone {phone_formatted} exists: {exists}')
        
        return JsonResponse({
            'valid': not exists,
            'exists': exists,
            'message': 'Этот номер телефона уже используется' if exists else 'Номер телефона доступен',
            'formatted_phone': phone_formatted
        })
    
    return JsonResponse({'valid': False, 'message': 'Недопустимый метод запроса'})

def hub(request):
    return render(request, 'hub.html', {'title': 'Хаб'})

@login_required
def profile(request):
    applications = Application.objects.all().order_by('-created_at')

    profile_form = ProfileEditForm(instance=request.user)

    print(f"Пользователь: {request.user.email} (ID: {request.user.id})")
    print(f"Найдено заявок: {applications.count()}")

    for app in applications:
        print(f"  - Заявка #{app.id}: {app.organization_name}, статус: {app.status}")

    for app in applications:
        if app.requirement_price:
            try:
                if isinstance(app.requirement_price, str) and ',' in app.requirement_price:
                    prices = app.requirement_price.split(',')
                    app.total_price = sum(float(p.strip()) for p in prices if p.strip())
                else:
                    app.total_price = float(app.requirement_price)
            except (ValueError, TypeError):
                app.total_price = app.requirement_price
        else:
            app.total_price = 0
    return render(request, 'profile.html', {
        'title': 'Профиль',
        'user': request.user,
        'applications': applications,
        'form': profile_form,
    })

@login_required
def create_team(request):
    applications = Application.objects.all().order_by('-created_at')
    
    return render(request, 'createTeam.html', {
        'title': 'Создание команды',
        'user': request.user,
        'applications': applications,
    })

def form_page(request):
    print(f"МЕТОД ЗАПРОСА: {request.method}")
    
    login_form = CustomAuthenticationForm()
    registration_form = CustomUserCreationForm()
    application_form = ApplicationForm()
    
    # Для авторизованных пользователей сразу показываем только форму заявки
    show_auth_forms = not request.user.is_authenticated

    # ОБРАБОТКА POST-ЗАПРОСОВ
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        # 1. ОБРАБОТКА ВХОДА
        if 'login_submit' in request.POST:
            # Если пользователь уже авторизован, редиректим на профиль
            if request.user.is_authenticated:
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'redirect_url': '/profile/',
                        'message': 'Вы уже авторизованы'
                    })
                return redirect('profile')
            
            login_form = CustomAuthenticationForm(request, data=request.POST)
            
            if login_form.is_valid():
                user = login_form.get_user()
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
                messages.success(request, 'Вход выполнен успешно!')
                
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'redirect_url': '/profile/',
                        'message': 'Вход выполнен успешно!'
                    })
                return redirect('profile')
            else:
                if is_ajax:
                    errors = {}
                    for field, field_errors in login_form.errors.items():
                        if field == '__all__':
                            errors['general'] = field_errors
                        else:
                            errors[field] = field_errors
                    return JsonResponse({
                        'success': False,
                        'errors': errors
                    })
                messages.error(request, 'Неверный email/телефон или пароль.')
        
        # 2. ОБРАБОТКА РЕГИСТРАЦИИ
        elif 'registration_submit' in request.POST:
            # Если пользователь уже авторизован, редиректим на профиль
            if request.user.is_authenticated:
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'redirect_url': '/profile/',
                        'message': 'Вы уже авторизованы'
                    })
                return redirect('profile')
            
            registration_form = CustomUserCreationForm(request.POST)
            
            if registration_form.is_valid():
                user = registration_form.save()
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
                messages.success(request, 'Регистрация прошла успешно!')
                
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'redirect_url': '/profile/',
                        'message': 'Регистрация прошла успешно!'
                    })
                return redirect('profile')
            else:
                if is_ajax:
                    errors = {}
                    for field, field_errors in registration_form.errors.items():
                        if field == '__all__':
                            errors['general'] = field_errors
                        else:
                            errors[field] = field_errors
                    return JsonResponse({
                        'success': False,
                        'errors': errors
                    })
                messages.error(request, 'Пожалуйста, исправьте ошибки в форме регистрации.')
        
        # 3. ОБРАБОТКА ЗАЯВКИ
        elif 'application_submit' in request.POST:
            print("="*50)
            print("ОБРАБОТКА ЗАЯВКИ")
            print("="*50)
            
            # Создаем копию POST данных для обработки
            post_data = request.POST.copy()
            
            # Обрабатываем requirement_name и requirement_price из формы
            requirement_names = request.POST.getlist('requirement_name[]')
            requirement_prices = request.POST.getlist('requirement_price[]')
            
            # Формируем JSON для требований
            requirements = []
            for i in range(len(requirement_names)):
                if requirement_names[i].strip():
                    req = {'name': requirement_names[i].strip()}
                    if i < len(requirement_prices) and requirement_prices[i].strip():
                        try:
                            req['price'] = float(requirement_prices[i].strip())
                        except ValueError:
                            req['price'] = requirement_prices[i].strip()
                    requirements.append(req)
            
            # Добавляем requirements_data в POST данные
            post_data['requirements_data'] = json.dumps(requirements)
            
            # Создаем форму с обновленными данными
            application_form = ApplicationForm(post_data, request.FILES)
            
            print(f"Требования (JSON): {requirements}")
            
            if application_form.is_valid():
                print("✅ Форма валидна")
                
                application = application_form.save(commit=False)
                
                # Привязываем пользователя, если авторизован
                if request.user.is_authenticated:
                    application.user = request.user
                
                # Данные уже обработаны в форме, просто сохраняем
                application.save()
                
                print(f"✅ Заявка #{application.id} сохранена")
                print(f"  - Навыки: {application.skill_list}")
                print(f"  - Ресурсы: {application.requirement_name}")
                print(f"  - Цены: {application.requirement_price}")
                
                messages.success(request, 'Заявка успешно отправлена!')
                
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'message': 'Заявка успешно отправлена!',
                        'redirect_url': '/profile/',
                        'application_id': application.id
                    })
                
                return redirect('profile')
                
            else:
                print("❌ Форма не валидна")
                print(f"Ошибки: {application_form.errors}")
                print(f"Ошибки полей: {application_form.errors.as_json()}")
                
                if is_ajax:
                    errors = {}
                    for field, field_errors in application_form.errors.items():
                        errors[field] = [str(error) for error in field_errors]
                    return JsonResponse({
                        'success': False,
                        'errors': errors,
                        'message': 'Пожалуйста, исправьте ошибки в форме'
                    })
                
                messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
        
        # 4. AJAX-ОБРАБОТКА (для совместимости)
        elif is_ajax and 'action' in request.POST:
            return handle_ajax_request(request)
    
    # ВОЗВРАТ ДЛЯ GET-ЗАПРОСА
    return render(request, 'formPage.html', {
        'title': 'Форма',
        'login_form': login_form,
        'registration_form': registration_form,
        'application_form': application_form,
        'messages': messages.get_messages(request),
        'show_auth_forms': show_auth_forms,
        'is_authenticated': request.user.is_authenticated
    })

def logout_view(request):
    """Выход из системы"""
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('hub')

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

from django.core.paginator import Paginator

@login_required
def all_projects(request):
    """Страница со всеми проектами платформы"""
    projects_list = Project.objects.exclude(status='draft').order_by('-created_at')
    
    # Поиск
    search_query = request.GET.get('q')
    if search_query:
        projects_list = projects_list.filter(
            models.Q(name__icontains=search_query) |
            models.Q(description__icontains=search_query) |
            models.Q(keywords__icontains=search_query)
        )
    
    paginator = Paginator(projects_list, 12)
    page_number = request.GET.get('page')
    projects = paginator.get_page(page_number)
    
    return render(request, 'all_projects.html', {'projects': projects})

@login_required
def project_list(request):
    """Список проектов пользователя"""
    # Проекты, где пользователь создатель
    created_projects = Project.objects.filter(creator=request.user).order_by('-created_at')
    
    # Проекты, где пользователь участник
    participating = ProjectParticipant.objects.filter(
        user=request.user, 
        status='active'
    ).select_related('project')
    participating_projects = [p.project for p in participating]
    
    # Приглашения для текущего пользователя
    invitations = ProjectInvitation.objects.filter(
        application__user=request.user,
        status='pending'
    ).select_related('project', 'invited_by', 'application')
    
    context = {
        'created_projects': created_projects,
        'participating_projects': participating_projects,
        'invitations': invitations,
    }
    return render(request, 'projectsList.html', context)

@login_required
def project_create(request):
    """
    Создание нового проекта с множественными требованиями к участникам
    """
    import logging
    logger = logging.getLogger(__name__)
    
    print("\n" + "="*80)
    print("🚀 СОЗДАНИЕ ПРОЕКТА - НАЧАЛО")
    print("="*80)
    print(f"📋 Метод запроса: {request.method}")
    print(f"👤 Пользователь: {request.user} (ID: {request.user.id})")
    print(f"📨 POST данные: {dict(request.POST)}")
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                print("\n📦 Начало транзакции базы данных")
                
                # Создаем проект
                print("\n📝 Создание проекта:")
                print(f"  - Название: {request.POST.get('name')}")
                print(f"  - Описание: {request.POST.get('description')[:50]}...")
                print(f"  - Ключевые слова: {request.POST.get('keywords')}")
                print(f"  - Начало: {request.POST.get('start_date')}")
                print(f"  - Окончание: {request.POST.get('end_date')}")
                print(f"  - Бюджет: {request.POST.get('budget')}")
                
                project = Project.objects.create(
                    name=request.POST.get('name'),
                    description=request.POST.get('description'),
                    keywords=request.POST.get('keywords', ''),
                    team_activities=request.POST.get('team_activities', ''),
                    work_conditions=request.POST.get('work_conditions', ''),
                    start_date=request.POST.get('start_date') or None,
                    end_date=request.POST.get('end_date') or None,
                    budget=request.POST.get('budget') or None,
                    status='draft',
                    creator=request.user
                )
                
                print(f"\n✅ ПРОЕКТ СОЗДАН:")
                print(f"  - ID: {project.id}")
                print(f"  - Название: {project.name}")
                print(f"  - В БД: {Project.objects.filter(id=project.id).exists()}")
                
                # Обработка множественных требований к участникам
                requirement_names = request.POST.getlist('requirement_name[]')
                requirement_levels = request.POST.getlist('requirement_level[]')
                requirement_counts = request.POST.getlist('requirement_count[]')
                requirement_mandatory = request.POST.getlist('requirement_mandatory[]')
                requirement_prices = request.POST.getlist('requirement_price[]')
                requirement_conditions = request.POST.getlist('requirement_condition[]')
                belbin_roles = request.POST.getlist('belbin_role[]')
                
                print(f"\n📋 Найдено требований: {len(requirement_names)}")
                print(f"  - Навыки: {requirement_names}")
                print(f"  - Уровни: {requirement_levels}")
                print(f"  - Количество: {requirement_counts}")
                print(f"  - Обязательные: {requirement_mandatory}")
                print(f"  - Цены: {requirement_prices}")
                print(f"  - Условия: {requirement_conditions}")
                print(f"  - Роли Белбина: {belbin_roles}")
                
                # Создаем требования для каждого навыка
                requirements_created = 0
                for i in range(len(requirement_names)):
                    if requirement_names[i].strip():
                        # Проверяем, обязательно ли требование
                        is_mandatory = False
                        if i < len(requirement_mandatory):
                            is_mandatory = (requirement_mandatory[i] == 'on' or 
                                           requirement_mandatory[i] == 'true')
                        
                        print(f"\n  📌 Создание требования #{i+1}:")
                        print(f"     - Навык: {requirement_names[i].strip()}")
                        print(f"     - Уровень: {requirement_levels[i] if i < len(requirement_levels) else 'не указан'}")
                        print(f"     - Роль Белбина: {belbin_roles[i] if i < len(belbin_roles) else 'не указана'}")
                        print(f"     - Количество: {requirement_counts[i] if i < len(requirement_counts) else 1}")
                        print(f"     - Обязательное: {is_mandatory}")
                        print(f"     - Цена: {requirement_prices[i] if i < len(requirement_prices) else 'не указана'}")
                        print(f"     - Условия: {requirement_conditions[i] if i < len(requirement_conditions) else 'не указаны'}")
                        
                        # Создаем требование
                        req = ProjectRequirement.objects.create(
                            project=project,
                            skill_name=requirement_names[i].strip(),
                            level_requirement=requirement_levels[i] if i < len(requirement_levels) and requirement_levels[i] else '',
                            belbin_role=belbin_roles[i] if i < len(belbin_roles) and belbin_roles[i] else '',
                            people_count=int(requirement_counts[i]) if i < len(requirement_counts) and requirement_counts[i] else 1,
                            is_mandatory=is_mandatory,
                            price=requirement_prices[i] if i < len(requirement_prices) and requirement_prices[i] else None,
                            work_condition=requirement_conditions[i] if i < len(requirement_conditions) and requirement_conditions[i] else ''
                        )
                        requirements_created += 1
                        print(f"     ✅ Требование #{requirements_created} создано (ID: {req.id})")
                
                print(f"\n📊 ИТОГИ:")
                print(f"  - Проект: {project.name} (ID: {project.id})")
                print(f"  - Требований создано: {requirements_created}")
                print(f"  - Всего требований в БД для проекта: {project.requirements.count()}")
                
                messages.success(request, f'Проект "{project.name}" успешно создан!')
                
                # AJAX ответ
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    print(f"\n📡 AJAX ответ отправляется")
                    return JsonResponse({
                        'success': True,
                        'redirect_url': f'/projects/{project.id}/',
                        'project_id': project.id,
                        'requirements_count': requirements_created,
                        'message': f'Проект "{project.name}" успешно создан'
                    })
                
                print(f"\n🔄 Редирект на страницу проекта: /projects/{project.id}/")
                return redirect('project_detail', project_id=project.id)
                
        except Exception as e:
            print(f"\n❌ ОШИБКА ПРИ СОЗДАНИИ ПРОЕКТА:")
            print(f"  - Тип ошибки: {type(e).__name__}")
            print(f"  - Сообщение: {str(e)}")
            import traceback
            print(f"  - Traceback: {traceback.format_exc()}")
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': str(e),
                    'error_type': type(e).__name__
                })
            messages.error(request, f'Ошибка при создании проекта: {e}')
    
    print("\n📄 GET запрос - отображение формы создания проекта")
    print("="*80 + "\n")
    
    # GET запрос - показываем форму
    return render(request, 'createProject.html', {
        'title': 'Создание проекта'
    })


# views.py (дополните существующую функцию project_detail для отображения требований)

@login_required
def project_detail(request, project_id):
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
    
    # Получаем все требования к проекту
    requirements = project.requirements.all().order_by('-is_mandatory', 'skill_name')
    
    # Группировка требований по обязательности
    mandatory_requirements = requirements.filter(is_mandatory=True)
    optional_requirements = requirements.filter(is_mandatory=False)
    
    # Подсчет общего количества требуемых специалистов
    total_people_needed = requirements.aggregate(
        total=models.Sum('people_count')
    )['total'] or 0
    
    # Участники проекта
    participants = project.participants.filter(status='active')
    
    # Приглашения
    invitations = project.invitations.all().order_by('-invited_at')
    
    context = {
        'project': project,
        'requirements': requirements,
        'mandatory_requirements': mandatory_requirements,
        'optional_requirements': optional_requirements,
        'total_people_needed': total_people_needed,
        'participants': participants,
        'invitations': invitations,
        'total_requirements_sum': project.get_total_requirements_sum(),
        'is_creator': is_creator,
        'is_participant': is_participant,
    }
    return render(request, 'project_detail.html', context)

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
                
                for i in range(len(requirement_names)):
                    if requirement_names[i].strip():
                        ProjectRequirement.objects.create(
                            project=project,
                            skill_name=requirement_names[i],
                            level_requirement=requirement_levels[i] if i < len(requirement_levels) else '',
                            people_count=int(requirement_counts[i]) if i < len(requirement_counts) else 1,
                            is_mandatory=(requirement_mandatory[i] == 'on') if i < len(requirement_mandatory) else False,
                            price=requirement_prices[i] if i < len(requirement_prices) and requirement_prices[i] else None,
                            work_condition=requirement_conditions[i] if i < len(requirement_conditions) else ''
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
    """Приглашение участника в проект"""
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
            
            return JsonResponse({
                'success': True,
                'invitation_id': invitation.id,
                'message': 'Приглашение отправлено'
            })
            
        except Application.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Заявка не найдена'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Неверный метод запроса'})


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

@login_required
def api_applications(request):
    """API для получения списка всех заявок"""
    applications = Application.objects.all().order_by('-created_at')
    data = []
    for app in applications:
        data.append({
            'id': app.id,
            'contact_first_name': app.contact_first_name,
            'contact_last_name': app.contact_last_name,
            'contact_email': app.contact_email,
            'contact_phone': app.contact_phone,
            'organization_name': app.organization_name,
            'age': app.age,
            'about_me': app.about_me,
            'team_role': app.get_team_role_display() if app.team_role else None,
            'skill_list': app.skill_list,
            'skills_json': app.skills_json,
        })
    return JsonResponse(data, safe=False)

from django.db.models import Q
from django.shortcuts import render
from .models_application import Application
from .models import CustomUser

def global_search(request):
    """Глобальный поиск по всему сайту"""
    from project.models import Project
    query = request.GET.get('q', '').strip()
    
    context = {
        'query': query,
        'projects': [],
        'applications': [],
        'users': [],
        'has_results': False
    }
    
    if query:
        projects = Project.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(keywords__icontains=query),
            status__in=['active', 'in_progress']
        ).order_by('-created_at')[:10]
        
        applications = Application.objects.filter(
            Q(organization_name__icontains=query) |
            Q(contact_first_name__icontains=query) |
            Q(contact_last_name__icontains=query) |
            Q(skill_list__icontains=query) |
            Q(technologies_text__icontains=query),
            status='approved'
        ).order_by('-created_at')[:10]
        
        users = CustomUser.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        ).order_by('username')[:10]
        
        context['projects'] = projects
        context['applications'] = applications
        context['users'] = users
        context['has_results'] = projects or applications or users
    
    return render(request, 'search_results.html', context)

@login_required
def edit_profile(request):
    """Редактирование профиля пользователя (AJAX через модальное окно)"""
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
            return redirect('profile')
    
    return redirect('profile')

def api_applications(request):
    """API для получения списка заявок (кандидатов)"""
    applications = Application.objects.filter(status='approved').order_by('-created_at')
    
    data = []
    for app in applications:
        data.append({
            'id': app.id,
            'contact_first_name': app.contact_first_name,
            'contact_last_name': app.contact_last_name,
            'contact_email': app.contact_email,
            'contact_phone': app.contact_phone,
            'organization_name': app.organization_name,
            'skill_list': app.skill_list,
            'age': app.age,
            'team_role': app.team_role,
            'team_role_display': dict(Application.TEAM_ROLE_CHOICES).get(app.team_role, ''),
            'status': app.status,
        })
    
    return JsonResponse(data, safe=False)