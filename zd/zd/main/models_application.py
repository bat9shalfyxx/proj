# main/models_application.py
from django.db import models
from django.conf import settings
from django.core.validators import ValidationError
import json
from decimal import Decimal

class Application(models.Model):
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

    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'В обработке'),
        ('approved', 'Одобрена'),
        ('rejected', 'Отклонена'),
    ]
    
    ACTIVITY_AREA_CHOICES = [
        ('it', 'Информационные технологии'),
        ('energy', 'Энергетика'),
        ('automation', 'Автоматика'),
        ('math', 'Математика'),
        ('economics', 'Экономика'),
        ('management', 'Менеджмент'),
        ('business_analysis', 'Бизнес-анализ'),
        ('other', 'Другое'),
    ]
    
    IT_SKILLS_CHOICES = [
        ('information_systems', 'Информационные системы'),
        ('design', 'Проектирование'),
        ('ui_development', 'Разработка пользовательского интерфейса'),
        ('server_development', 'Разработка серверной части'),
        ('client_development', 'Клиентская часть'),
        ('other', 'Другое'),
    ]
    
    TECHNOLOGY_CHOICES = [
        ('programming_language', 'Язык программирования'),
        ('database', 'СУБД'),
        ('framework', 'Фреймворк'),
        ('library', 'Библиотека'),
        ('other', 'Другое'),
    ]
    
    TEAM_ROLE_CHOICES = [
        ('developer', 'Разработчик'),
        ('frontend', 'Frontend-разработчик'),
        ('backend', 'Backend-разработчик'),
        ('fullstack', 'Fullstack-разработчик'),
        ('mobile', 'Мобильный разработчик'),
        ('devops', 'DevOps-инженер'),
        ('designer', 'Дизайнер'),
        ('ui_ux', 'UI/UX-дизайнер'),
        ('project_manager', 'Проектный менеджер'),
        ('product_manager', 'Продуктовый менеджер'),
        ('team_lead', 'Тимлид'),
        ('tech_lead', 'Технический лид'),
        ('analyst', 'Аналитик'),
        ('qa', 'QA-инженер'),
        ('tester', 'Тестировщик'),
        ('marketing', 'Маркетолог'),
        ('sales', 'Менеджер по продажам'),
        ('support', 'Саппорт'),
        ('other', 'Другое'),
    ]
    
    WORK_SCHEDULE_CHOICES = [
        ('full_time', 'Полная занятость'),
        ('part_time', 'Частичная занятость'),
        ('flexible', 'Гибкий график'),
        ('remote', 'Удаленная работа'),
        ('project_work', 'Проектная работа'),
        ('other', 'Другое'),
    ]
    
    def get_absolute_url(self):
        return f'/news/{self.id}'
    
    activity_area = models.CharField(
        'Область деятельности',
        max_length=50,
        choices=ACTIVITY_AREA_CHOICES,
        default='it',
        blank=True
    )
    activity_area_other = models.CharField(
        'Другая область деятельности',
        max_length=255,
        blank=True,
        default=''
    )
    
    it_skill = models.CharField(
        'Ключевые навыки в IT',
        max_length=50,
        choices=IT_SKILLS_CHOICES,
        default='information_systems',
        blank=True
    )
    it_skill_other = models.CharField(
        'Другие ключевые навыки',
        max_length=255,
        blank=True,
        default=''
    )

    
    technologies_json = models.JSONField('Технологии (структурированные)', default=list, blank=True)
    technologies_text = models.TextField('Технологии (текст)', blank=True, default='')
    technology = models.CharField(
        'Знание технологий',
        max_length=50,
        choices=TECHNOLOGY_CHOICES,
        default='programming_language',
        blank=True
    )
    technology_other = models.CharField(
        'Другие технологии',
        max_length=255,
        blank=True,
        default=''
    )
    technology_details = models.TextField(
        'Детальное описание технологий',
        blank=True,
        default='',
        help_text='Перечислите конкретные технологии, языки, СУБД, фреймворки и т.д.'
    )
    
    team_role = models.CharField(
        'Ваша специальность',  # меняем здесь
        max_length=50,
        choices=TEAM_ROLE_CHOICES,
        default='developer',
        blank=True
    )
    belbin_role = models.CharField(
        'Роль в команде (по Белбину)',
        max_length=30,
        choices=BELBIN_ROLE_CHOICES,
        blank=True,
        default=''
    )
    team_role_other = models.CharField(
        'Другая роль',
        max_length=255,
        blank=True,
        default=''
    )
    
    leaderid_link = models.URLField('Ссылка на LeaderID', blank=True, default='')
    elibrary_link = models.URLField('Ссылка на Elibrary', blank=True, default='')
    github_link = models.URLField('Ссылка на GitHub', blank=True, default='')
    project_examples = models.TextField(
        'Примеры проектов',
        blank=True,
        default='',
        help_text='Опишите ваши проекты, можно добавить ссылки'
    )
    work_experience = models.TextField(
        'Опыт работы',
        blank=True,
        default='',
        help_text='Опишите ваш опыт работы'
    )
    driver_license = models.BooleanField('Наличие водительских прав', default=False)
    
    expected_salary = models.DecimalField(
        'Ожидаемое вознаграждение (₽)',
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    work_schedule = models.CharField(
        'График работы',
        max_length=20,
        choices=WORK_SCHEDULE_CHOICES,
        default='full_time',
        blank=True
    )
    work_schedule_other = models.CharField(
        'Другой график',
        max_length=255,
        blank=True,
        default=''
    )
    required_equipment = models.TextField(
        'Требуемое оборудование',
        blank=True,
        default='',
        help_text='Какое оборудование необходимо для работы'
    )
    
    collaboration_expectations = models.TextField(
        'Ожидание от сотрудничества',
        blank=True,
        default='',
        help_text='Что вы ожидаете от сотрудничества?'
    )
    
    skill_list = models.TextField('Ваши навыки', default='JS, REACT, TypeScript', blank=True)
    skills_json = models.JSONField('Навыки (структурированные)', default=list, blank=True)
    
    # organization_name = models.CharField('Наименование организации', max_length=255, default='NewOrg')
    # organization_inn = models.CharField('ИНН организации', max_length=12, default='1000000000')
    # organization_website = models.URLField('Сайт организации', blank=True, default='http://NewOrg.com')

    contact_first_name = models.CharField('Имя', max_length=100, default='Тимур')
    contact_last_name = models.CharField('Фамилия', max_length=100, default='Шокиров')
    contact_middle_name = models.CharField('Отчество', max_length=100, blank=True)
    contact_phone = models.CharField('Телефон', max_length=20, default='+79879879292')
    contact_email = models.EmailField('Электронная почта', default='ya@gmail.com')
    
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name='Пользователь'
    )
    
    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Заявка от {self.organization_name} ({self.created_at.strftime('%d.%m.%Y')})"
    
    def save(self, *args, **kwargs):
        if self.technologies_json and not self.technologies_text:
            techs_text = ', '.join([tech.get('name', '') for tech in self.technologies_json if tech.get('name')])
            self.technologies_text = techs_text
        elif self.technologies_text and not self.technologies_json:
            try:
                if self.technologies_text.startswith('[') and self.technologies_text.endswith(']'):
                    self.technologies_json = json.loads(self.technologies_text)
                else:
                    techs = [t.strip() for t in self.technologies_text.split(',') if t.strip()]
                    self.technologies_json = [{'name': tech, 'level': 'unspecified'} for tech in techs]
            except:
                pass
        
        super().save(*args, **kwargs)

    def get_technologies_by_level(self):
        """Возвращает технологии, сгруппированные по уровням"""
        techs_by_level = {
            'expert': [],
            'senior': [],
            'middle': [],
            'junior': [],
            'beginner': [],
            'unspecified': []
        }
        
        if self.technologies_json:
            for tech in self.technologies_json:
                level = tech.get('level', 'unspecified')
                if level in techs_by_level:
                    techs_by_level[level].append(tech)
                else:
                    techs_by_level['unspecified'].append(tech)
        
        return techs_by_level
    
    def get_activity_area_display_full(self):
        """Полное отображение области деятельности"""
        if self.activity_area == 'other' and self.activity_area_other:
            return self.activity_area_other
        return dict(self.ACTIVITY_AREA_CHOICES).get(self.activity_area, '')
    
    def get_it_skill_display_full(self):
        """Полное отображение IT навыка"""
        if self.it_skill == 'other' and self.it_skill_other:
            return self.it_skill_other
        return dict(self.IT_SKILLS_CHOICES).get(self.it_skill, '')
    
    def get_technology_display_full(self):
        """Полное отображение технологии"""
        if self.technology == 'other' and self.technology_other:
            return self.technology_other
        return dict(self.TECHNOLOGY_CHOICES).get(self.technology, '')
    
    def get_team_role_display_full(self):
        """Полное отображение роли"""
        if self.team_role == 'other' and self.team_role_other:
            return self.team_role_other
        return dict(self.TEAM_ROLE_CHOICES).get(self.team_role, '')