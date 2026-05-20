from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import RegexValidator
from django.conf import settings
import random
import re
import string
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    """Менеджер для кастомной модели пользователя"""
    
    def create_user(self, email, password=None, **extra_fields):
        """
        Создает обычного пользователя
        """
        if not email:
            raise ValueError('Email обязателен')
        
        email = self.normalize_email(email)
        
        # Генерируем username из email, если не указан
        username = extra_fields.get('username')
        if not username:
            username = email.split('@')[0]
            username = re.sub(r'[^a-zA-Z0-9_]', '', username)
            
            if not username:
                username = 'user_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            
            # Проверяем уникальность
            original_username = username
            counter = 1
            while self.model.objects.filter(username=username).exists():
                username = f'{original_username}{counter}'
                counter += 1
            
            extra_fields['username'] = username
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """
        Создает суперпользователя
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True.')
        
        # Генерируем username для суперпользователя
        username = extra_fields.get('username')
        if not username:
            username = email.split('@')[0]
            username = re.sub(r'[^a-zA-Z0-9_]', '', username)
            
            if not username:
                username = 'admin_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            
            extra_fields['username'] = username
        
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    middle_name = models.CharField('Отчество', max_length=150, blank=True)
    email = models.EmailField('Электронная почта', unique=True)

    phone_regex = RegexValidator(
        regex=r'^\+7\d{10}$',
        message="Номер телефона должен быть в формате: '+79991234567'"
    )
    phone_number = models.CharField(
        'Номер телефона',
        validators=[phone_regex],
        max_length=12,
        blank=True,
        null=True
    )
    profile_image = models.ImageField(
        'Фото профиля',
        upload_to='profile_images/%Y/%m/',
        blank=True,
        null=True
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # username не требуется при создании
    
    objects = CustomUserManager()
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower()
        
        if self.phone_number == '':
            self.phone_number = None
        
        # Убеждаемся, что username не пустой
        if not self.username and self.email:
            username = self.email.split('@')[0]
            username = re.sub(r'[^a-zA-Z0-9_]', '', username)
            
            if not username:
                username = 'user_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            
            # Проверяем уникальность
            original_username = username
            counter = 1
            while CustomUser.objects.filter(username=username).exists():
                username = f'{original_username}{counter}'
                counter += 1
            
            self.username = username
        
        super().save(*args, **kwargs)

# Импортируем Application из отдельного файла
from .models_application import Application

# Модель проекта
class Project(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('active', 'Активный'),
        ('in_progress', 'В работе'),
        ('completed', 'Завершен'),
        ('on_hold', 'Приостановлен'),
        ('cancelled', 'Отменен'),
    ]
    
    name = models.CharField('Название проекта', max_length=255)
    description = models.TextField('Описание проекта')
    keywords = models.CharField('Ключевые слова', max_length=500, blank=True, 
                               help_text='Введите через запятую')
    team_activities = models.TextField('Чем планирует заниматься команда', blank=True)
    work_conditions = models.TextField('Условия работы', blank=True)
    start_date = models.DateField('Дата начала', null=True, blank=True)
    end_date = models.DateField('Дата окончания', null=True, blank=True)
    budget = models.DecimalField('Бюджет проекта', max_digits=15, 
                                decimal_places=2, null=True, blank=True)
    status = models.CharField('Статус', max_length=20, 
                             choices=STATUS_CHOICES, default='draft')
    
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='main_created_projects',
        verbose_name='Создатель проекта'
    )
    
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    
    def get_keywords_list(self):
        if self.keywords:
            return [k.strip() for k in self.keywords.split(',') if k.strip()]
        return []
    
    def get_total_requirements_sum(self):
        """Сумма всех стоимостей требований к проекту"""
        from django.db.models import Sum
        total = self.requirements.aggregate(total=Sum('price'))['total'] or 0
        return total

class ProjectRequirement(models.Model):
    SKILL_LEVEL_CHOICES = [
        ('beginner', 'Начинающий'),
        ('middle', 'Продвинутый'),
        ('expert', 'Эксперт'),
    ]
    
    BELBIN_ROLE_CHOICES = [
        ('implementer', 'Исполнитель'),
        ('coordinator', 'Координатор'),
        ('shaper', 'Формирователь'),
        ('plant', 'Генератор идей'),
        ('resource_investigator', 'Разведчик'),
        ('teamworker', 'Душа команды'),
        ('monitor_evaluator', 'Аналитик'),
        ('completer_finisher', 'Педантичность'),
        ('specialist', 'Специалист'),
    ]
    
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='requirements',
        verbose_name='Проект'
    )
    
    skill_name = models.CharField('Название навыка', max_length=200)
    level_requirement = models.CharField('Требуемый уровень', max_length=20,
                                        choices=SKILL_LEVEL_CHOICES, blank=True)
    belbin_role = models.CharField('Роль по Белбину', max_length=30,
                                  choices=BELBIN_ROLE_CHOICES, blank=True)
    work_condition = models.CharField('Условие работы', max_length=500, blank=True)
    people_count = models.PositiveIntegerField('Количество человек', default=1)
    is_mandatory = models.BooleanField('Обязательное', default=True)
    price = models.DecimalField('Стоимость', max_digits=12, 
                               decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.skill_name} ({self.get_level_requirement_display()}) - {self.people_count} чел."


class ProjectInvitation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает ответа'),
        ('accepted', 'Принято'),
        ('declined', 'Отклонено'),
        ('cancelled', 'Отменено'),
    ]
    
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='invitations',
        verbose_name='Проект'
    )
    application = models.ForeignKey(
        Application, 
        on_delete=models.CASCADE, 
        related_name='main_project_invitations',
        verbose_name='Заявка'
    )
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='main_sent_invitations',
        verbose_name='Пригласил'
    )
    
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='pending')
    message = models.TextField('Сопроводительное сообщение', blank=True)
    invited_at = models.DateTimeField('Дата приглашения', auto_now_add=True)
    responded_at = models.DateTimeField('Дата ответа', null=True, blank=True)
    
    email_sent = models.BooleanField('Письмо отправлено', default=False)
    email_sent_at = models.DateTimeField('Дата отправки письма', null=True, blank=True)

    class Meta:
        verbose_name = 'Приглашение'
        verbose_name_plural = 'Приглашения'
        ordering = ['-invited_at']
        unique_together = ['project', 'application']
    
    def __str__(self):
        app_name = f"{self.application.contact_first_name} {self.application.contact_last_name}"
        return f"{app_name} -> {self.project.name}"
    
    def send_invitation_email(self):
        """Отправка письма с приглашением"""
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags
        from django.conf import settings
        
        candidate_email = self.application.contact_email
        inviter_name = self.invited_by.get_full_name() or self.invited_by.username
        
        # Формируем ссылки для ответа
        accept_url = f"{settings.SITE_URL}/invitation/{self.id}/respond/?action=accept"
        decline_url = f"{settings.SITE_URL}/invitation/{self.id}/respond/?action=decline"
        
        context = {
            'project_name': self.project.name,
            'project_description': self.project.description[:200] if self.project.description else '',
            'inviter_name': inviter_name,
            'inviter_email': self.invited_by.email,
            'message': self.message,
            'accept_url': accept_url,
            'decline_url': decline_url,
            'candidate_name': f"{self.application.contact_first_name} {self.application.contact_last_name}",
        }
        
        try:
            # Рендерим HTML шаблон письма
            html_message = render_to_string('emails/invitation_email.html', context)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject=f'Приглашение в проект "{self.project.name}"',
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[candidate_email],
                html_message=html_message,
                fail_silently=False,
            )
            self.email_sent = True
            self.email_sent_at = timezone.now()
            self.save()
            return True
        except Exception as e:
            print(f"Ошибка отправки письма: {e}")
            return False
    
    def accept(self):
        self.status = 'accepted'
        self.responded_at = timezone.now()
        self.save()
        
        ProjectParticipant.objects.get_or_create(
            project=self.project,
            application=self.application,
            defaults={
                'user': self.application.user,
                'full_name': f"{self.application.contact_first_name} {self.application.contact_last_name}",
                'email': self.application.contact_email,
                'phone': self.application.contact_phone,
                'skills': self.application.skill_list,
                'requirements': self.application.requirement_name,
                'requirement_price': self.application.requirement_price,
                'status': 'active'
            }
        )
    
    def decline(self):
        self.status = 'declined'
        self.responded_at = timezone.now()
        self.save()
    
    def cancel(self):
        self.status = 'cancelled'
        self.save()

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=ProjectInvitation)
def create_notification_on_invitation(sender, instance, created, **kwargs):
    """Создает уведомление при создании нового приглашения"""
    if created:
        from main.models import Notification
        Notification.objects.create(
            user=instance.application.user,
            invitation=instance,
            title=f'Новое приглашение в проект "{instance.project.name}"',
            message=f'Пользователь {instance.invited_by.get_full_name() or instance.invited_by.username} приглашает вас присоединиться к проекту "{instance.project.name}"',
            type='invitation',
            is_read=False
        )

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('invitation', 'Приглашение'),
        ('project_update', 'Обновление проекта'),
        ('comment', 'Комментарий'),
        ('system', 'Системное'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Пользователь'
    )
    invitation = models.ForeignKey(
        'ProjectInvitation',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    title = models.CharField('Заголовок', max_length=255)
    message = models.TextField('Сообщение')
    type = models.CharField('Тип', max_length=20, choices=NOTIFICATION_TYPES, default='system')
    is_read = models.BooleanField('Прочитано', default=False)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"

class ProjectParticipant(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активный'),
        ('inactive', 'Неактивный'),
        ('left', 'Покинул проект'),
    ]
    
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='participants',
        verbose_name='Проект'
    )
    application = models.ForeignKey(
        Application, 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        related_name='main_project_memberships',  # ИЗМЕНЕНО: добавлен префикс main_
        verbose_name='Заявка'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        related_name='main_participating_projects',  # ИЗМЕНЕНО: добавлен префикс main_
        verbose_name='Пользователь'
    )
    
    full_name = models.CharField('ФИО', max_length=255)
    email = models.EmailField('Email')
    phone = models.CharField('Телефон', max_length=20, blank=True)
    skills = models.TextField('Навыки', blank=True)
    requirements = models.TextField('Требования к ресурсам', blank=True)
    requirement_price = models.CharField('Цена ресурсов', max_length=255, blank=True)
    role = models.CharField('Роль в проекте', max_length=200, default='Участник')
    
    status = models.CharField('Статус', max_length=20, 
                             choices=STATUS_CHOICES, default='active')
    
    joined_at = models.DateTimeField('Дата присоединения', auto_now_add=True)
    left_at = models.DateTimeField('Дата ухода', null=True, blank=True)
    
    contribution_description = models.TextField('Описание вклада', blank=True)
    rating = models.PositiveSmallIntegerField('Оценка', null=True, blank=True,
                                             help_text='Оценка от 1 до 5')
    
    class Meta:
        verbose_name = 'Участник проекта'
        verbose_name_plural = 'Участники проекта'
        unique_together = ['project', 'application']
    
    def __str__(self):
        return f"{self.full_name} в {self.project.name}"
    
    def leave_project(self):
        self.status = 'left'
        self.left_at = timezone.now()
        self.save()
    
    def get_requirement_price_sum(self):
        if self.requirement_price:
            try:
                prices = str(self.requirement_price).split(',')
                return sum(float(p.strip()) for p in prices if p.strip())
            except (ValueError, AttributeError):
                pass
        return 0


class ProjectFile(models.Model):
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name='Проект'
    )
    
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='main_uploaded_files',  # ИЗМЕНЕНО: добавлен префикс main_
        verbose_name='Загрузил'
    )
    
    file = models.FileField('Файл', upload_to='project_files/%Y/%m/%d/')
    filename = models.CharField('Имя файла', max_length=255)
    file_size = models.IntegerField('Размер файла (байт)')
    description = models.CharField('Описание', max_length=255, blank=True)
    uploaded_at = models.DateTimeField('Дата загрузки', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Файл проекта'
        verbose_name_plural = 'Файлы проекта'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.filename


class ProjectComment(models.Model):
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Проект'
    )
    
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='main_project_comments',  # ИЗМЕНЕНО: добавлен префикс main_
        verbose_name='Автор'
    )
    
    text = models.TextField('Текст комментария')
    
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE,
        null=True, 
        blank=True, 
        related_name='replies',
        verbose_name='Ответ на'
    )
    
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    
    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.author} - {self.created_at.strftime('%d.%m.%Y %H:%M')}"