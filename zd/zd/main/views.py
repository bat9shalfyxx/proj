from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import CustomUser
import re
import logging
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

def index(request):
    login_form = CustomAuthenticationForm()
    registration_form = CustomUserCreationForm()
    
    if request.method == 'POST':
        # Проверяем AJAX запрос
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return handle_ajax_request(request, login_form, registration_form)
        
        # Обычная обработка POST запроса
        if 'login_submit' in request.POST:
            login_form = CustomAuthenticationForm(request, data=request.POST)
            
            if login_form.is_valid():
                username = login_form.cleaned_data.get('username')
                password = login_form.cleaned_data.get('password')
                
                user = authenticate(request, username=username, password=password)
                
                if user is not None:
                    user.backend = 'main.backends.EmailOrPhoneBackend'
                    login(request, user)
                    messages.success(request, 'Вход выполнен успешно!')
                    return redirect('hub')
                else:
                    login_form.add_error(None, 'Неверный email/телефон или пароль.')
                    
        elif 'registration_submit' in request.POST:
            registration_form = CustomUserCreationForm(request.POST)
            
            if registration_form.is_valid():
                user = registration_form.save()
                user.backend = 'main.backends.EmailOrPhoneBackend'
                login(request, user)
                messages.success(request, 'Регистрация прошла успешно!')
                return redirect('hub')
    
    return render(request, 'main/index.html', {
        'login_form': login_form,
        'registration_form': registration_form
    })

def handle_ajax_request(request, login_form, registration_form):
    """Обработка AJAX запросов для формы входа"""
    if 'login_submit' in request.POST:
        login_form = CustomAuthenticationForm(request, data=request.POST)
        
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                user.backend = 'main.backends.EmailOrPhoneBackend'
                login(request, user)
                return JsonResponse({
                    'success': True,
                    'redirect_url': '/hub/',
                    'message': 'Вход выполнен успешно!'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Неверный email/телефон или пароль.'
                })
        else:
            # Возвращаем ошибки валидации
            errors = login_form.errors.as_json()
            return JsonResponse({
                'success': False,
                'error': 'Пожалуйста, исправьте ошибки в форме.',
                'errors': errors
            })
    
    return JsonResponse({'success': False, 'error': 'Неизвестный запрос'})

@csrf_exempt
def validate_email(request):
    try:
        email = request.GET.get('email', '').strip().lower()
        logger.info(f'Validating email: {email}')
        
        if not email:
            return JsonResponse({'exists': False})
        
        exists = CustomUser.objects.filter(email__iexact=email).exists()
        logger.info(f'Email {email} exists: {exists}')
        
        return JsonResponse({'exists': exists})
    except Exception as e:
        logger.error(f'Error validating email: {e}')
        return JsonResponse({'exists': False})

@csrf_exempt
def validate_phone(request):
    try:
        phone = request.GET.get('phone', '').strip()
        logger.info(f'Validating phone: {phone}')
        
        if not phone:
            return JsonResponse({'exists': False})
        
        # Нормализация номера
        phone = re.sub(r'[^\d+]', '', phone)
        if not phone.startswith('+7'):
            if phone.startswith('8'):
                phone = '+7' + phone[1:]
            elif phone.startswith('7'):
                phone = '+' + phone
            else:
                phone = '+7' + phone
        
        logger.info(f'Normalized phone: {phone}')
        
        exists = CustomUser.objects.filter(phone_number=phone).exists()
        logger.info(f'Phone {phone} exists: {exists}')
        
        return JsonResponse({'exists': exists})
    except Exception as e:
        logger.error(f'Error validating phone: {e}')
        return JsonResponse({'exists': False})

@login_required
def hub(request):
    return render(request, 'main/hubPage.html', {'title': 'Хаб'})

@login_required
def profile(request):
    return render(request, 'main/profilePage.html', {'title': 'Профиль'})