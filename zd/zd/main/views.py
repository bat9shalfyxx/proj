from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ApplicationForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import CustomUser, Application
import re
import logging
from django.template.loader import render_to_string
from django.views.generic import DetailView

logger = logging.getLogger(__name__)

class NewDetailView(DetailView):
    model = Application
    template_name = 'main/index.html'
    context_object_name = 'Application'

def index(request):
    login_form = CustomAuthenticationForm()
    registration_form = CustomUserCreationForm()
    application_form = ApplicationForm()
    application = Application.objects.all()
    # application_list = list(application.values())
    # context = {
    #     'application_json': application_list
    # }

    if request.method == 'POST':
        # Обработка формы заявки
        if 'application_submit' in request.POST:
            application_form = ApplicationForm(request.POST)
            if application_form.is_valid():
                application = application_form.save(commit=False)
                
                # Если пользователь авторизован, связываем заявку с ним
                if request.user.is_authenticated:
                    application.user = request.user
                
                application.save()
                messages.success(request, 'Заявка успешно отправлена!')
                
                # Для AJAX запросов
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': 'Заявка успешно отправлена!'
                    })
                return redirect('home')
            else:
                # Для AJAX запросов
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'errors': application_form.errors.get_json_data()
                    })
        
        # Остальная обработка форм (логин и регистрация)
        elif 'login_submit' in request.POST:
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
        'registration_form': registration_form,
        'application_form': application_form,
        'application':application
    })

@login_required
def hub(request):
    return render(request, 'main/hubPage.html', {'title': 'Хаб'})

@login_required
def profile(request):
    # Получаем заявки пользователя
    user_applications = Application.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'main/profilePage.html', {
        'title': 'Профиль',
        'applications': user_applications
    })

# Функция для просмотра всех заявок (для администраторов)
@login_required
def applications_list(request):
    if not request.user.is_staff:
        return redirect('home')
    
    applications = Application.objects.all().order_by('-created_at')
    return render(request, 'main/applications_list.html', {
        'applications': applications
    })

# Функция для изменения статуса заявки
@login_required
def update_application_status(request, application_id):
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Доступ запрещен'})
    
    if request.method == 'POST':
        try:
            application = Application.objects.get(id=application_id)
            new_status = request.POST.get('status')
            
            if new_status in dict(Application.STATUS_CHOICES):
                application.status = new_status
                application.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Статус заявки обновлен'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Неверный статус'
                })
                
        except Application.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Заявка не найдена'
            })
    
    return JsonResponse({'success': False, 'error': 'Неверный метод запроса'})

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