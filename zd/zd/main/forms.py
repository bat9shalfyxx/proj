from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import CustomUser, Application
import re
import json

class ApplicationForm(forms.ModelForm):
    skills_data = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Application
        fields = [
            # Организация
            'organization_name', 'organization_inn', 'organization_website',
            
            # О себе и возраст
            'age', 'about_me',
            
            # Роль и навыки
            'team_role', 'skill_list', 'skills_json',
            
            # Ресурсы
            'requirement_name', 'requirement_price',
            
            # Контакты
            'contact_first_name', 'contact_last_name', 'contact_middle_name',
            'contact_phone', 'contact_email',
        ]
        widgets = {
            # Организация
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
            
            # Возраст
            'age': forms.NumberInput(attrs={
                'placeholder': 'Ваш возраст',
                'class': 'form-input age-input',
                'min': 14,
                'max': 100
            }),
            
            # О себе
            'about_me': forms.Textarea(attrs={
                'placeholder': 'Расскажите о себе: опыт, образование, цели, интересы...',
                'class': 'form-input about-textarea',
                'rows': 5
            }),
            
            # Роль
            'team_role': forms.Select(attrs={
                'class': 'form-input role-select',
            }),
            
            # Контакты
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
            
            # Ресурсы
            'requirement_name': forms.TextInput(attrs={
                'placeholder': 'Название ресурса',
                'class': 'requirement-name'
            }),
            'requirement_price': forms.NumberInput(attrs={
                'placeholder': 'Цена ресурса',
                'class': 'requirement-price'
            })
        }

    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Убираем метки
        for field_name in self.fields:
            self.fields[field_name].label = ''
        
        # Настройка полей
        self.fields['team_role'].empty_label = 'Выберите роль (необязательно)'
        self.fields['age'].required = False
        self.fields['about_me'].required = False
        
        # Загрузка существующих навыков
        if self.instance and self.instance.pk and self.instance.skills_json:
            self.initial['skills_data'] = json.dumps(self.instance.skills_json)
        elif self.instance and self.instance.skill_list:
            skills = [s.strip() for s in self.instance.skill_list.split(',') if s.strip()]
            skills_json = [{'name': skill, 'level': 'unspecified'} for skill in skills]
            self.initial['skills_data'] = json.dumps(skills_json)

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
                    raise forms.ValidationError("Неверный формат данных навыков")
                
                # Валидация каждого навыка
                for skill in skills:
                    if not isinstance(skill, dict):
                        raise forms.ValidationError("Каждый навык должен быть объектом")
                    if 'name' not in skill or not skill['name'].strip():
                        raise forms.ValidationError("Название навыка обязательно")
                    
                    # Проверка уровня
                    valid_levels = ['expert', 'senior', 'middle', 'junior', 'beginner', 'unspecified']
                    if 'level' in skill and skill['level'] not in valid_levels:
                        skill['level'] = 'unspecified'
                
                return skills
            except json.JSONDecodeError:
                raise forms.ValidationError("Ошибка парсинга JSON")
        return []
     
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Сохраняем навыки
        skills_data = self.cleaned_data.get('skills_data')
        if skills_data:
            try:
                instance.skills_json = json.loads(skills_data)
            except:
                pass
        
        if commit:
            instance.save()
        
        return instance
    #
    #
    def clean_requirements(self):
        requirements_data = self.cleaned_data.get('requirements')
        
        if not requirements_data:
            return []
        try:
            requirements_list_data = json.loads(requirements_data)
            requirements_list = json.dumps(requirements_list_data)

            if not isinstance(requirements_list, list):
                raise forms.ValidationError("Некорректный формат данных для требований. Ожидается список.")
                
            for item in requirements_list:
                if not isinstance(item, dict):
                    raise forms.ValidationError("Некорректный формат записи в требованиях. Ожидается объект.")
                
                if 'resource_name' not in item or 'price' not in item:
                    raise forms.ValidationError("Каждое требование должно содержать 'resource_name' и 'price'.")
                
                if not isinstance(item['resource_name'], str) or not item['resource_name']:
                    raise forms.ValidationError("Поле 'resource_name' должно быть непустой строкой.")
                
                try:
                    item['price'] = forms.DecimalField().clean(str(item['price']))
                except forms.ValidationError:
                    raise forms.ValidationError(f"Некорректная цена для ресурса '{item.get('resource_name', 'неизвестно')}'.")
            
            return requirements_list

        except json.JSONDecodeError:
            raise forms.ValidationError("Некорректный формат JSON. Пожалуйста, проверьте правильность ввода.")
        except Exception as e:
            raise forms.ValidationError(f"Ошибка при обработке требований: {e}")
    #
    #

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
                    'Неверный email/телефон/логин или пароль.',
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
                    'Неверный email/телефон/логин или пароль.',
                    code='invalid_login'
                )
            
           
            self.confirm_login_allowed(user)
            
           
            self.user_cache = user
        
        return cleaned_data
    
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
            # 'profile_image': forms.ImageField(
            #     label='Фото профиля:',
            #     required=False
            # )
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
                
                import re
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
