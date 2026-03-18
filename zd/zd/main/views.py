# main/views.py - исправленная версия

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from main.models_application import Application
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ApplicationForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import CustomUser
import re
import logging
import json

def form_page(request):
    if request.method == 'POST' and request.POST.get('application_submit'):
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            
            # Если пользователь авторизован, связываем заявку с ним
            if request.user.is_authenticated:
                application.user = request.user
            
            # Обработка технологий (если есть)
            technologies_data = request.POST.get('technologies_data')
            if technologies_data:
                try:
                    application.technologies_json = json.loads(technologies_data)
                except:
                    pass
            
            application.save()
            
            messages.success(request, 'Заявка успешно отправлена!')
            return redirect('profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
    
    # ВАЖНО: создаем формы для входа и регистрации
    login_form = CustomAuthenticationForm()
    registration_form = CustomUserCreationForm()
    
    # Если это POST запрос с формой входа
    if request.method == 'POST' and request.POST.get('login_submit'):
        login_form = CustomAuthenticationForm(request, data=request.POST)
        if login_form.is_valid():
            user = login_form.get_user()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            messages.success(request, 'Вход выполнен успешно!')
            return redirect('profile')
    
    # Если это POST запрос с формой регистрации
    if request.method == 'POST' and request.POST.get('registration_submit'):
        registration_form = CustomUserCreationForm(request.POST, request.FILES)
        if registration_form.is_valid():
            user = registration_form.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('profile')
    
    # Создаем форму заявки для GET запроса
    application_form = ApplicationForm()
    
    return render(request, 'formPage.html', {
        'title': 'Форма',
        'application_form': application_form,
        'login_form': login_form,
        'registration_form': registration_form,
        'user_authenticated': request.user.is_authenticated,
        'messages': messages.get_messages(request)
    })

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
    applications = Application.objects.filter(user=request.user).order_by('-created_at')

    print(f"Пользователь: {request.user.email} (ID: {request.user.id})")
    print(f"Найдено заявок: {applications.count()}")
    for app in applications:
        print(f"  - Заявка #{app.id}: статус: {app.status}")

    for app in applications:
        app.display_salary = app.expected_salary if app.expected_salary else 0
        
        app.total_price = app.expected_salary if app.expected_salary else 0
        
        if app.technologies_json:
            app.technologies_count = len(app.technologies_json)
            app.main_technologies = [t.get('name', '') for t in app.technologies_json[:3]]
        else:
            app.technologies_count = 0
            app.main_technologies = []
    
    return render(request, 'profile.html', {
        'title': 'Профиль',
        'user': request.user,
        'applications': applications,
    })

@login_required
def create_team(request):
    applications = Application.objects.all().order_by('-created_at')
    
    for app in applications:
        app.display_salary = app.expected_salary if app.expected_salary else 0
        
        if app.technologies_json:
            app.technologies_by_level = app.get_technologies_by_level()
        else:
            app.technologies_by_level = {}
    
    return render(request, 'createTeam.html', {
        'title': 'Создание команды',
        'user': request.user,
        'applications': applications,
    })


def logout_view(request):
    """Выход из системы"""
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('hub')