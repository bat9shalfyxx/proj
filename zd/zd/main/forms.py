from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import CustomUser, Application, Project, ProjectRequirement
import re
import json
from django.utils.translation import gettext_lazy as _


class CustomAuthenticationForm(AuthenticationForm):
    """
    Единая форма аутентификации с русскими сообщениями и поддержкой
    email/телефон/логин
    """
    
    # Кастомные сообщения об ошибках (русские)
    error_messages = {
        'invalid_login': _(
            "Неверный email/телефон или пароль. Пожалуйста, проверьте введённые данные."
        ),
        'inactive': _("Этот аккаунт заблокирован. Обратитесь к администратору."),
    }
    
    # Переопределяем поля с нужными плейсхолдерами
    username = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'placeholder': 'Телефон, электронная почта или логин',
            'autocomplete': 'on',
            'class': 'form-input',
            'required': 'required'
        })
    )
    password = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Введите пароль',
            'autocomplete': 'on',
            'class': 'form-input',
            'required': 'required'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = ''
        self.fields['password'].label = ''
    
    def normalize_username(self, username):
        """Нормализует введенное значение для поиска пользователя"""
        if '@' in username:
            return username.lower()
        
        phone = re.sub(r'[^\d+]', '', username)
        if phone.startswith('8'):
            phone = '+7' + phone[1:]
        elif phone.startswith('7'):
            phone = '+' + phone
        elif not phone.startswith('+7'):
            phone = '+7' + phone
        
        return phone
    
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        
        if username and password:
            normalized_username = self.normalize_username(username)
            
            from django.contrib.auth import get_user_model
            from django.db.models import Q
            User = get_user_model()
            
            try:
                user = User.objects.get(
                    Q(email=normalized_username) | 
                    Q(phone_number=normalized_username) |
                    Q(username=username)
                )
            except User.DoesNotExist:
                raise ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login'
                )
            except User.MultipleObjectsReturned:
                user = User.objects.filter(
                    Q(email=normalized_username) | 
                    Q(phone_number=normalized_username) |
                    Q(username=username)
                ).first()
            
            if not user.check_password(password):
                raise ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login'
                )
            
            self.confirm_login_allowed(user)
            self.user_cache = user
        
        return cleaned_data


class ApplicationForm(forms.ModelForm):
    skills_data = forms.CharField(widget=forms.HiddenInput(), required=False)
    requirements_data = forms.CharField(widget=forms.HiddenInput(), required=False, initial='[]')

    class Meta:
        model = Application
        fields = [
            # Личная информация
            'contact_last_name', 'contact_first_name', 'contact_middle_name',
            'contact_phone', 'contact_email', 'age', 'about_me',
            
            # Профессиональная информация
            'team_role', 'skill_list', 'skills_json',
            
            # Организация
            'organization_name', 'organization_inn', 'organization_website',
        ]
        widgets = {
            # Личная информация
            'contact_last_name': forms.TextInput(attrs={
                'placeholder': 'Фамилия',
                'class': 'form-input',
                'required': 'required'
            }),
            'contact_first_name': forms.TextInput(attrs={
                'placeholder': 'Имя',
                'class': 'form-input',
                'required': 'required'
            }),
            'contact_middle_name': forms.TextInput(attrs={
                'placeholder': 'Отчество',
                'class': 'form-input'
            }),
            'contact_phone': forms.TextInput(attrs={
                'placeholder': 'Телефон',
                'class': 'form-input',
                'required': 'required'
            }),
            'contact_email': forms.EmailInput(attrs={
                'placeholder': 'Электронная почта',
                'class': 'form-input',
                'required': 'required'
            }),
            'age': forms.NumberInput(attrs={
                'placeholder': 'Ваш возраст',
                'class': 'form-input age-input',
                'min': 14,
                'max': 100
            }),
            'about_me': forms.Textarea(attrs={
                'placeholder': 'Расскажите о себе: опыт, образование, цели, интересы...',
                'class': 'form-input about-textarea',
                'rows': 5
            }),
            
            # Профессиональная информация
            'team_role': forms.Select(attrs={
                'class': 'form-input role-select',
            }),
            
            # Организация
            'organization_name': forms.TextInput(attrs={
                'placeholder': 'Наименование организации',
                'class': 'form-input',
                'required': 'required'
            }),
            'organization_inn': forms.TextInput(attrs={
                'placeholder': 'ИНН организации',
                'class': 'form-input',
                'required': 'required'
            }),
            'organization_website': forms.URLInput(attrs={
                'placeholder': 'Сайт организации',
                'class': 'form-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Убираем метки
        for field_name in self.fields:
            self.fields[field_name].label = ''
        
        # Настройка полей
        self.fields['team_role'].empty_label = 'Выберите роль в команде'
        self.fields['age'].required = False
        self.fields['about_me'].required = False
        self.fields['organization_website'].required = False
        
        # Загрузка существующих навыков
        if self.instance and self.instance.pk:
            if self.instance.skills_json:
                self.initial['skills_data'] = json.dumps(self.instance.skills_json)
            elif self.instance.skill_list:
                skills = [s.strip() for s in self.instance.skill_list.split(',') if s.strip()]
                skills_json = [{'name': skill, 'level': 'unspecified'} for skill in skills]
                self.initial['skills_data'] = json.dumps(skills_json)
            
            # Загрузка существующих требований
            if self.instance.requirement_name or self.instance.requirement_price:
                requirements = []
                names = self.instance.requirement_name.split(', ') if self.instance.requirement_name else []
                prices = self.instance.requirement_price.split(', ') if self.instance.requirement_price else []
                
                for i in range(max(len(names), len(prices))):
                    req = {}
                    if i < len(names):
                        req['name'] = names[i]
                    if i < len(prices):
                        req['price'] = prices[i]
                    if req:
                        requirements.append(req)
                
                self.initial['requirements_data'] = json.dumps(requirements)

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age and (age < 14 or age > 100):
            raise ValidationError('Возраст должен быть от 14 до 100 лет')
        return age
    
    def clean_skills_data(self):
        skills_data = self.cleaned_data.get('skills_data')
        if skills_data:
            try:
                skills = json.loads(skills_data)
                if not isinstance(skills, list):
                    raise ValidationError("Неверный формат данных навыков")
                
                # Валидация каждого навыка
                for skill in skills:
                    if not isinstance(skill, dict):
                        raise ValidationError("Каждый навык должен быть объектом")
                    if 'name' not in skill or not skill['name'].strip():
                        raise ValidationError("Название навыка обязательно")
                    
                    # Проверка уровня
                    valid_levels = ['expert', 'senior', 'middle', 'junior', 'beginner', 'unspecified']
                    if 'level' in skill and skill['level'] not in valid_levels:
                        skill['level'] = 'unspecified'
                
                return skills
            except json.JSONDecodeError:
                raise ValidationError("Ошибка парсинга JSON")
        return []
    
    def clean_requirements_data(self):
        requirements_data = self.cleaned_data.get('requirements_data', '[]')
        if requirements_data:
            try:
                requirements = json.loads(requirements_data)
                if not isinstance(requirements, list):
                    raise ValidationError("Неверный формат данных требований")
                
                # Валидация каждого требования
                for req in requirements:
                    if not isinstance(req, dict):
                        raise ValidationError("Каждое требование должно быть объектом")
                    
                    # Проверка названия ресурса
                    if 'name' in req and req['name'] and not isinstance(req['name'], str):
                        raise ValidationError("Название ресурса должно быть строкой")
                    
                    # Проверка цены
                    if 'price' in req and req['price']:
                        try:
                            float(req['price'])
                        except (ValueError, TypeError):
                            raise ValidationError(f"Некорректная цена для ресурса '{req.get('name', 'неизвестно')}'")
                
                return requirements
            except json.JSONDecodeError:
                raise ValidationError("Ошибка парсинга JSON требований")
        return []

    def clean_organization_inn(self):
        inn = self.cleaned_data.get('organization_inn')
        if inn:
            # Проверка формата ИНН (10 или 12 цифр)
            inn_clean = re.sub(r'\D', '', inn)
            if not re.match(r'^\d{10}$', inn_clean) and not re.match(r'^\d{12}$', inn_clean):
                raise ValidationError('ИНН должен содержать 10 или 12 цифр.')
        return inn
    
    def clean_contact_phone(self):
        phone = self.cleaned_data.get('contact_phone')
        if phone:
            # Нормализация номера телефона
            phone = re.sub(r'[^\d+]', '', phone)
            if phone.startswith('8'):
                phone = '+7' + phone[1:]
            elif phone.startswith('7'):
                phone = '+' + phone
            elif not phone.startswith('+7') and phone.startswith('+'):
                pass
            elif not phone.startswith('+'):
                phone = '+7' + phone
            
            # Проверка формата
            if not re.match(r'^\+7\d{10}$', phone):
                raise ValidationError('Номер телефона должен быть в формате: +7XXXXXXXXXX')
        
        return phone
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Проверка, что хотя бы одно из полей навыков заполнено
        skill_list = cleaned_data.get('skill_list')
        skills_data = cleaned_data.get('skills_data')
        
        if not skill_list and (not skills_data or skills_data == '[]'):
            raise ValidationError('Заполните хотя бы один навык')
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Сохраняем навыки из JSON
        skills_data = self.cleaned_data.get('skills_data')
        if skills_data:
            try:
                instance.skills_json = json.loads(skills_data) if isinstance(skills_data, str) else skills_data
                
                # Обновляем skill_list из JSON
                if instance.skills_json:
                    skills_text = ', '.join([skill.get('name', '') for skill in instance.skills_json if skill.get('name')])
                    instance.skill_list = skills_text
            except:
                pass
        
        # Сохраняем требования
        requirements_data = self.cleaned_data.get('requirements_data', [])
        if requirements_data:
            try:
                requirements = json.loads(requirements_data) if isinstance(requirements_data, str) else requirements_data
                
                # Формируем строки для сохранения
                names = [req.get('name', '') for req in requirements if req.get('name')]
                prices = [str(req.get('price', '')) for req in requirements if req.get('price')]
                
                instance.requirement_name = ', '.join(names) if names else ''
                instance.requirement_price = ', '.join(prices) if prices else ''
            except:
                pass
        
        if commit:
            instance.save()
        
        return instance


class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label='Придумайте пароль',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Придумайте пароль',
            'autocomplete': 'on',
            'class': 'form-input'
        }),
        help_text='Минимум 8 символов'
    )
    
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Подтвердите пароль',
            'autocomplete': 'on',
            'class': 'form-input'
        })
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'last_name', 'first_name', 'middle_name', 'email', 'phone_number', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Логин (только латинские буквы и цифры)',
                'class': 'form-input'
            }),
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
                'placeholder': 'Номер мобильного телефона (необязательно)',
                'class': 'form-input'
            }),
        }
        help_texts = {
            'password1': 'Минимум 8 символов',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['username'].required = False
        self.fields['last_name'].required = False
        self.fields['first_name'].required = False
        self.fields['middle_name'].required = False
        self.fields['phone_number'].required = False
        self.fields['email'].required = True
        
        for field_name in self.fields:
            self.fields[field_name].label = ''
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            email = self.cleaned_data.get('email', '')
            if email:
                username = email.split('@')[0]
                username = re.sub(r'[^a-zA-Z0-9_]', '', username)
                
                if not username:
                    import random
                    import string
                    username = 'user_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower()
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                raise ValidationError('Введите корректный адрес электронной почты.')
            
            if CustomUser.objects.filter(email=email).exists():
                raise ValidationError('Пользователь с таким email уже существует.')
        
        return email
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            phone_number = re.sub(r'[^\d+]', '', phone_number)
            if phone_number.startswith('8'):
                phone_number = '+7' + phone_number[1:]
            elif phone_number.startswith('7'):
                phone_number = '+' + phone_number
            elif not phone_number.startswith('+7'):
                phone_number = '+7' + phone_number
            
            if len(phone_number) != 12:
                raise ValidationError('Номер телефона должен содержать 11 цифр после +7.')
            
            if CustomUser.objects.filter(phone_number=phone_number).exists():
                raise ValidationError('Пользователь с таким номером телефона уже существует.')
        
        return phone_number
    
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if password1 and len(password1) < 8:
            raise ValidationError('Пароль должен содержать минимум 8 символов.')
        return password1
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError({
                'password2': 'Пароли не совпадают.'
            })
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        if not user.username:
            username = self.cleaned_data.get('username')
            if not username:
                email = self.cleaned_data.get('email', '')
                if email:
                    username = email.split('@')[0]
                    username = re.sub(r'[^a-zA-Z0-9_]', '', username)
                    
                    if not username:
                        import random
                        import string
                        username = 'user_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            
            from .models import CustomUser
            original_username = username
            counter = 1
            while CustomUser.objects.filter(username=username).exists():
                username = f'{original_username}{counter}'
                counter += 1
            
            user.username = username
        
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.middle_name = self.cleaned_data.get('middle_name', '')
        user.phone_number = self.cleaned_data.get('phone_number', '')
        
        if commit:
            user.save()
        
        return user


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'name', 'description', 'keywords', 'team_activities', 
            'work_conditions', 'start_date', 'end_date', 'budget'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Разработка мобильного приложения'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Опишите идею, цели, задачи и ожидаемые результаты проекта...'
            }),
            'keywords': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Python, веб-разработка, искусственный интеллект'
            }),
            'team_activities': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Например: разработка backend, создание дизайна, тестирование...'
            }),
            'work_conditions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Формат работы (удаленно/офис), график, требования к участникам...'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'budget': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: 500000',
                'min': '0',
                'step': '0.01'
            }),
        }
        help_texts = {
            'keywords': 'Введите ключевые слова через запятую',
        }


class ProjectRequirementForm(forms.ModelForm):
    class Meta:
        model = ProjectRequirement
        fields = [
            'skill_name', 'level_requirement', 'belbin_role',
            'people_count', 'is_mandatory', 'price', 'work_condition'
        ]
        widgets = {
            'skill_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'например: Python, аналитика, дизайн'
            }),
            'level_requirement': forms.Select(attrs={'class': 'form-control'}),
            'belbin_role': forms.Select(attrs={'class': 'form-control'}),
            'people_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'value': '1'
            }),
            'is_mandatory': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: 50000',
                'min': '0',
                'step': '0.01'
            }),
            'work_condition': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'например: Работа в выходные, командировки'
            }),
        }


class QuickRequirementForm(forms.Form):
    skill_name = forms.CharField(max_length=200)
    level = forms.ChoiceField(choices=ProjectRequirement.SKILL_LEVEL_CHOICES, required=False)
    people_count = forms.IntegerField(min_value=1, initial=1)


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'profile_image']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Имя пользователя'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Имя'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Фамилия'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'Email'
            }),
            'profile_image': forms.FileInput(attrs={
                'class': 'form-input-file',
                'accept': 'image/*'
            }),
        }