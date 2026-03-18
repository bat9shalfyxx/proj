from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from main.models_application import Application

User = settings.AUTH_USER_MODEL

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
    
    team_activities = models.TextField('Чем планирует заниматься команда', blank=True)
    
    work_conditions = models.TextField('Условия работы', blank=True)
    
    start_date = models.DateField('Дата начала', null=True, blank=True)
    end_date = models.DateField('Дата окончания', null=True, blank=True)
    
    budget = models.DecimalField('Бюджет проекта', max_digits=15, 
                                decimal_places=2, null=True, blank=True)

    status = models.CharField('Статус', max_length=20, 
                             choices=STATUS_CHOICES, default='draft')
    
    keywords = models.CharField(
        'Ключевые слова',
        max_length=500,
        blank=True,
        help_text='Введите ключевые слова через запятую'
    )

    creator = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='created_projects',
        verbose_name='Создатель проекта'
    )
    
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    
    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_total_requirements_sum(self):
#сумма требований к проекту
        total = 0
        for participant in self.participants.filter(status='active'):
            if participant.application and participant.application.requirement_price:
                try:
                    prices = str(participant.application.requirement_price).split(',')
                    total += sum(float(p.strip()) for p in prices if p.strip())
                except (ValueError, AttributeError):
                    pass
        return total
    
    def get_active_participants_count(self):
        #Количество активных участников
        return self.participants.filter(status='active').count()

class ProjectRequirement(models.Model):
    #Требования к участникам проекта
    
    SKILL_LEVEL_CHOICES = [
        ('beginner', 'Начинающий'),
        ('junior', 'Junior'),
        ('middle', 'Middle'),
        ('senior', 'Senior'),
        ('expert', 'Эксперт'),
    ]
    
    belbin_role = models.CharField(
        'Требуемая роль по Белбину',
        max_length=30,
        choices=BELBIN_ROLE_CHOICES,
        blank=True,
        help_text='Необязательное поле. Выберите роль, которая требуется для данного навыка'
    )

    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='requirements',
        verbose_name='Проект'
    )
    
    skill_name = models.CharField('Название навыка', max_length=200, blank=True)
    level_requirement = models.CharField('Требуемый уровень', max_length=20,
                                        choices=SKILL_LEVEL_CHOICES, blank=True)
    
    work_condition = models.CharField('Условие работы', max_length=500, blank=True,
                                      help_text='Например: "Работа в выходные", "Командировки"')

    people_count = models.PositiveIntegerField('Количество человек', default=1)

    is_mandatory = models.BooleanField('Обязательное', default=True)
    
    price = models.DecimalField('Стоимость', max_digits=12, 
                               decimal_places=2, null=True, blank=True,
                               help_text='Для ресурсных требований')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Требование к участнику'
        verbose_name_plural = 'Требования к участникам'
        ordering = ['-is_mandatory', 'skill_name']
    
    def __str__(self):
        if self.skill_name:
            return f"{self.skill_name} ({self.level_requirement}) - {self.people_count} чел."
        return f"Условие: {self.work_condition}"
    
    def get_matching_applications(self):
        #Поиск заявок, подходящих под это требование
        from main.models_application import Application
        
        if not self.skill_name:
            return Application.objects.none()
        
        return Application.objects.filter(
            skill_list__icontains=self.skill_name
        ).exclude(
            project_memberships__project=self.project
        ).distinct()

class ProjectInvitation(models.Model):
    #Приглашения в проект
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
        related_name='project_invitations',
        verbose_name='Заявка'
    )
    invited_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sent_invitations',
        verbose_name='Пригласил'
    )
    
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='pending')
    message = models.TextField('Сопроводительное сообщение', blank=True)
    
    invited_at = models.DateTimeField('Дата приглашения', auto_now_add=True)
    responded_at = models.DateTimeField('Дата ответа', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Приглашение'
        verbose_name_plural = 'Приглашения'
        ordering = ['-invited_at']
        unique_together = ['project', 'application']  # Чтобы не приглашать дважды
    
    def __str__(self):
        app_name = f"{self.application.contact_first_name} {self.application.contact_last_name}"
        return f"{app_name} -> {self.project.name}"
    
    def accept(self):
        """Принять приглашение"""
        self.status = 'accepted'
        self.responded_at = timezone.now()
        self.save()
        
        # Создаем запись об участнике
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
        #Отклонить приглашение
        self.status = 'declined'
        self.responded_at = timezone.now()
        self.save()
    
    def cancel(self):
        #Отменить приглашение
        self.status = 'cancelled'
        self.save()


class ProjectParticipant(models.Model):
    #Участники проекта (из приглашений)
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
        related_name='project_memberships',
        verbose_name='Заявка'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        related_name='participating_projects',
        verbose_name='Пользователь'
    )
    
    # Данные участника (копия из заявки)
    full_name = models.CharField('ФИО', max_length=255)
    email = models.EmailField('Email')
    phone = models.CharField('Телефон', max_length=20, blank=True)
    skills = models.TextField('Навыки', blank=True)
    requirements = models.TextField('Требования к ресурсам', blank=True)
    requirement_price = models.CharField('Цена ресурсов', max_length=255, blank=True)
    
    # Роль в проекте
    role = models.CharField('Роль в проекте', max_length=200)
    
    # Статус
    status = models.CharField('Статус', max_length=20, 
                             choices=STATUS_CHOICES, default='active')
    
    # Даты
    joined_at = models.DateTimeField('Дата присоединения', auto_now_add=True)
    left_at = models.DateTimeField('Дата ухода', null=True, blank=True)
    
    # Оценка работы
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
        #Покинуть проект
        self.status = 'left'
        self.left_at = timezone.now()
        self.save()
    
    def get_requirement_price_sum(self):
        #Получить сумму требований участника
        if self.requirement_price:
            try:
                prices = str(self.requirement_price).split(',')
                return sum(float(p.strip()) for p in prices if p.strip())
            except (ValueError, AttributeError):
                pass
        return 0


class ProjectFile(models.Model):
    #Файлы проекта
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name='Проект'
    )
    
    uploaded_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='uploaded_files',
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
    #Комментарии к проекту
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Проект'
    )
    
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='project_comments',
        verbose_name='Автор'
    )
    
    text = models.TextField('Текст комментария')
    
    # Для ответов на комментарии
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


