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
            
            application.save()
            
            messages.success(request, 'Заявка успешно отправлена!')
            return redirect('profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
    else:
        form = ApplicationForm()
    
    return render(request, 'formPage.html', {
        'application_form': form
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
    print(f"POST данные: {request.POST}")
    print(f"Headers: {request.headers.get('X-Requested-With')}")
    
    login_form = CustomAuthenticationForm()
    registration_form = CustomUserCreationForm()
    application_form = ApplicationForm()

    if request.method == 'POST':
        
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if 'login_submit' in request.POST:
            login_form = CustomAuthenticationForm(request, data=request.POST)
            
            if login_form.is_valid():
                user = login_form.get_user()
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
                messages.success(request, 'Вход выполнен успешно!')
                
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'redirect': '/profile/'
                    })
                return redirect('profile')
            else:
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'errors': login_form.errors.get_json_data()
                    })
                messages.error(request, 'Неверный email/телефон или пароль.')
        
        elif 'registration_submit' in request.POST:
            registration_form = CustomUserCreationForm(request.POST)
            
            if registration_form.is_valid():
                user = registration_form.save()
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
                messages.success(request, 'Регистрация прошла успешно!')
                
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'redirect': '/profile/'
                    })
                return redirect('profile')
            else:
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'errors': registration_form.errors.get_json_data()
                    })
                messages.error(request, 'Пожалуйста, исправьте ошибки в форме регистрации.')
        
        elif 'application_submit' in request.POST:
            print("="*50)
            print("ОБРАБОТКА ЗАЯВКИ")
            print("="*50)
            
            application_form = ApplicationForm(request.POST)
            
            if application_form.is_valid():
                print("✅ Форма валидна")
                
        
                application = application_form.save(commit=False)
                
            
                if request.user.is_authenticated:
                    application.user = request.user
                
           
                requirement_names = request.POST.getlist('requirement_name')
                requirement_prices = request.POST.getlist('requirement_price')
                
                print(f"Ресурсы: {requirement_names} - {requirement_prices}")
                
   
                valid_names = [name for name in requirement_names if name and name.strip()]
                valid_prices = [price for price in requirement_prices if price and price.strip()]
                
                if valid_names:
                    application.requirement_name = ', '.join(valid_names)
                if valid_prices:
                    application.requirement_price = ', '.join(valid_prices)
   
                application.save()
                print(f"✅ Заявка #{application.id} сохранена")
                print(f"requirement_name: {application.requirement_name}")
                print(f"requirement_price: {application.requirement_price}")
                
                messages.success(request, 'Заявка успешно отправлена!')
                

                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'message': 'Заявка успешно отправлена!',
                        'redirect': '/profile/'
                    })
                
                return redirect('profile')
                
            else:
                print("❌ Форма не валидна")
                print(f"Ошибки: {application_form.errors}")
                
   
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'errors': application_form.errors.get_json_data()
                    })
                
                messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')

        elif is_ajax and 'action' in request.POST:
     
            return handle_ajax_request(request)
    
    # GET запрос
    return render(request, 'formPage.html', {
        'title': 'Форма',
        'login_form': login_form,
        'registration_form': registration_form,
        'application_form': application_form,
        'messages': messages.get_messages(request)
    })

def logout_view(request):
    """Выход из системы"""
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('hub')