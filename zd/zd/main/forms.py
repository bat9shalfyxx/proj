from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import CustomUser, Application
import re

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = [
            'organization_name', 'organization_inn', 'organization_website',
            'solution_name', 'solution_description', 'solution_experience',
            'contact_first_name', 'contact_last_name', 'contact_middle_name',
            'contact_phone', 'contact_email'
        ]
        widgets = {
            'organization_name': forms.TextInput(attrs={
                'placeholder': 'Наименование организации',
                'class': 'form-input'
            }),
            'organization_inn': forms.TextInput(attrs={
                'placeholder': 'ИНН организации',
                'class': 'form-input'
            }),
            'organization_website': forms.URLInput(attrs={
                'placeholder': 'Сайт организации',
                'class': 'form-input'
            }),
            'solution_name': forms.TextInput(attrs={
                'placeholder': 'Краткое наименование',
                'class': 'form-input'
            }),
            'solution_description': forms.Textarea(attrs={
                'placeholder': 'Описание предлагаемого решения',
                'class': 'form-input',
                'rows': 4
            }),
            'solution_experience': forms.Textarea(attrs={
                'placeholder': 'Релевантный опыт применения подобного решения',
                'class': 'form-input',
                'rows': 4
            }),
            'contact_first_name': forms.TextInput(attrs={
                'placeholder': 'Имя',
                'class': 'form-input'
            }),
            'contact_last_name': forms.TextInput(attrs={
                'placeholder': 'Фамилия',
                'class': 'form-input'
            }),
            'contact_middle_name': forms.TextInput(attrs={
                'placeholder': 'Отчество',
                'class': 'form-input'
            }),
            'contact_phone': forms.TextInput(attrs={
                'placeholder': 'Телефон',
                'class': 'form-input'
            }),
            'contact_email': forms.EmailInput(attrs={
                'placeholder': 'Электронная почта',
                'class': 'form-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Убираем labels для чистого отображения
        for field_name in self.fields:
            self.fields[field_name].label = ''
    
    def clean_organization_inn(self):
        inn = self.cleaned_data.get('organization_inn')
        if inn:
            # Проверка формата ИНН (10 или 12 цифр)
            if not re.match(r'^\d{10}$', inn) and not re.match(r'^\d{12}$', inn):
                raise ValidationError('ИНН должен содержать 10 или 12 цифр.')
        return inn
    
    def clean_contact_phone(self):
        phone = self.cleaned_data.get('contact_phone')
        if phone:
            # Нормализация номера телефона
            phone = re.sub(r'[^\d+]', '', phone)
            if not phone.startswith('+7'):
                if phone.startswith('8'):
                    phone = '+7' + phone[1:]
                elif phone.startswith('7'):
                    phone = '+' + phone
                else:
                    phone = '+7' + phone
            
            # Проверка длины
            if len(phone) != 12:
                raise ValidationError('Номер телефона должен содержать 11 цифр после +7.')
        
        return phone

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label='Email или телефон',
        widget=forms.TextInput(attrs={
            'placeholder': 'Телефон, электронная почта',
            'autocomplete': 'on',
            'class': 'form-input'
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Введите пароль',
            'autocomplete': 'on',
            'class': 'form-input'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = ''
        self.fields['password'].label = ''
    
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        
        if username and password:
            # Проверяем существование пользователя
            from django.contrib.auth import get_user_model
            UserModel = get_user_model()
            
            try:
                # Пытаемся найти по email
                user = UserModel.objects.get(email=username)
            except UserModel.DoesNotExist:
                try:
                    # Пытаемся найти по номеру телефона
                    from .backends import EmailOrPhoneBackend
                    backend = EmailOrPhoneBackend()
                    phone = backend.normalize_phone(username)
                    user = UserModel.objects.get(phone_number=phone)
                except (UserModel.DoesNotExist, ValueError):
                    user = None
            
            if user and not user.check_password(password):
                raise ValidationError('Неверный пароль.')
        
        return cleaned_data

class CustomUserCreationForm(UserCreationForm):
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Подтвердите пароль',
            'autocomplete': 'on',
            'class': 'form-input'
        }),
        help_text='Введите тот же пароль, что и выше, для проверки.'
    )
    
    class Meta:
        model = CustomUser
        fields = ('last_name', 'first_name', 'middle_name', 'email', 'phone_number', 'password1', 'password2')
        widgets = {
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Фамилия',
                'class': 'form-input'
            }),
            'first_name': forms.TextInput(attrs={
                'placeholder': 'Имя', 
                'class': 'form-input'
            }),
            'middle_name': forms.TextInput(attrs={
                'placeholder': 'Отчество',
                'class': 'form-input'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Электронная почта*',
                'class': 'form-input'
            }),
            'phone_number': forms.TextInput(attrs={
                'placeholder': 'Номер мобильного телефона*',
                'class': 'form-input'
            }),
            'password1': forms.PasswordInput(attrs={
                'placeholder': 'Придумайте пароль',
                'autocomplete': 'on',
                'class': 'form-input'
            }),
        }
        help_texts = {
            'password1': 'Минимум 8 символов',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем поля необязательными
        self.fields['last_name'].required = False
        self.fields['first_name'].required = False
        self.fields['middle_name'].required = False
        
        # Обязательные поля
        self.fields['email'].required = True
        self.fields['phone_number'].required = True
        
        # Убираем labels для чистого отображения
        for field_name in self.fields:
            self.fields[field_name].label = ''
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Проверка формата email
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                raise ValidationError('Введите корректный адрес электронной почты.')
            
            # Проверка уникальности в БД
            if CustomUser.objects.filter(email=email).exists():
                raise ValidationError('Пользователь с таким email уже существует.')
        
        return email
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            # Нормализация номера телефона
            phone_number = re.sub(r'[^\d+]', '', phone_number)
            if not phone_number.startswith('+7'):
                if phone_number.startswith('8'):
                    phone_number = '+7' + phone_number[1:]
                elif phone_number.startswith('7'):
                    phone_number = '+' + phone_number
                else:
                    phone_number = '+7' + phone_number
            
            # Проверка длины
            if len(phone_number) != 12:
                raise ValidationError('Номер телефона должен содержать 11 цифр после +7.')
            
            # Проверка уникальности в БД
            if CustomUser.objects.filter(phone_number=phone_number).exists():
                raise ValidationError('Пользователь с таким номером телефона уже существует.')
        
        return phone_number
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError({
                'password2': 'Пароли не совпадают.'
            })
        
        return cleaned_data