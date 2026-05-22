# main/models_application.py
from django.db import models
from django.conf import settings
from django.core.validators import ValidationError, RegexValidator
import json
import re
from decimal import Decimal

class Application(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'В обработке'),
        ('approved', 'Одобрена'),
        ('rejected', 'Отклонена'),
    ]
    
    TEAM_ROLE_CHOICES = [
        ('visionary', 'Генератор идей'),
        ('implementer', 'Исполнитель'),
        ('leader', 'Лидер'),
        ('organizer', 'Организатор'),
        ('analyst', 'Аналитик'),
        ('communicator', 'Коммуникатор'),
        ('perfectionist', 'Контролер качества'),
        ('resource_investigator', 'Исследователь ресурсов'),
        ('developer', 'Разработчик'),
        ('designer', 'Дизайнер'),
        ('project_manager', 'Проектный менеджер'),
        ('other', 'Другое'),
    ]
    
    # Личная информация
    contact_last_name = models.CharField('Фамилия', max_length=100)
    contact_first_name = models.CharField('Имя', max_length=100)
    contact_middle_name = models.CharField('Отчество', max_length=100, blank=True)
    
    phone_regex = RegexValidator(
        regex=r'^\+7\d{10}$',
        message="Номер телефона должен быть в формате: '+7XXXXXXXXXX'"
    )
    contact_phone = models.CharField('Телефон', validators=[phone_regex], max_length=12)
    contact_email = models.EmailField('Электронная почта')
    
    age = models.PositiveIntegerField('Возраст', null=True, blank=True)
    about_me = models.TextField('О себе', blank=True, default='')
    
    # Профессиональная информация
    team_role = models.CharField(
        'Роль в команде', 
        max_length=50, 
        choices=TEAM_ROLE_CHOICES, 
        blank=True,
        null=True
    )
    
    # Навыки (в двух форматах - для совместимости)
    skill_list = models.TextField('Ваши навыки', blank=True, default='')
    skills_json = models.JSONField('Навыки (структурированные)', default=list, blank=True)
    
    # Организация
    organization_name = models.CharField('Наименование организации', max_length=255)
    organization_inn = models.CharField('ИНН организации', max_length=12)
    organization_website = models.URLField('Сайт организации', blank=True)
    
    # Ресурсы
    requirement_name = models.TextField('Названия ресурсов', blank=True, default='')
    requirement_price = models.TextField('Цены ресурсов', blank=True, default='')
    
    # Системные поля
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    
    # Связь с пользователем
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name='Пользователь',
        related_name='applications'
    )
    
    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Заявка #{self.id} от {self.organization_name} ({self.created_at.strftime('%d.%m.%Y')})"
    
    def save(self, *args, **kwargs):
        # Синхронизация skills_json и skill_list
        if self.skills_json and not self.skill_list:
            # Из JSON в текст
            skills_text = ', '.join([
                skill.get('name', '') for skill in self.skills_json 
                if skill.get('name')
            ])
            self.skill_list = skills_text
            
        elif self.skill_list and not self.skills_json:
            # Из текста в JSON
            try:
                # Проверяем, не JSON ли это случайно
                if self.skill_list.strip().startswith('[') and self.skill_list.strip().endswith(']'):
                    self.skills_json = json.loads(self.skill_list)
                else:
                    skills = [s.strip() for s in self.skill_list.split(',') if s.strip()]
                    self.skills_json = [{'name': skill, 'level': 'unspecified'} for skill in skills]
            except:
                pass
        
        # Нормализация ИНН (убираем лишние символы)
        if self.organization_inn:
            self.organization_inn = re.sub(r'\D', '', self.organization_inn)
        
        super().save(*args, **kwargs)
    
    def get_skills_list(self):
        """Возвращает список навыков"""
        if self.skills_json:
            return self.skills_json
        elif self.skill_list:
            return [{'name': s.strip(), 'level': 'unspecified'} 
                   for s in self.skill_list.split(',') if s.strip()]
        return []
    
    def get_skills_by_level(self):
        """Возвращает навыки, сгруппированные по уровням"""
        skills_by_level = {
            'expert': [],
            'senior': [],
            'middle': [],
            'junior': [],
            'beginner': [],
            'unspecified': []
        }
        
        skills = self.get_skills_list()
        for skill in skills:
            level = skill.get('level', 'unspecified')
            if level in skills_by_level:
                skills_by_level[level].append(skill)
            else:
                skills_by_level['unspecified'].append(skill)
        
        return skills_by_level
    
    def get_requirements_list(self):
        """Возвращает список требований"""
        requirements = []
        
        names = self.requirement_name.split(', ') if self.requirement_name else []
        prices = self.requirement_price.split(', ') if self.requirement_price else []
        
        for i in range(max(len(names), len(prices))):
            req = {}
            if i < len(names) and names[i]:
                req['name'] = names[i]
            if i < len(prices) and prices[i]:
                try:
                    req['price'] = float(prices[i])
                except ValueError:
                    req['price'] = prices[i]
            if req:
                requirements.append(req)
        
        return requirements
    
    def get_total_budget(self):
        """Возвращает общую сумму бюджета"""
        total = 0
        prices = self.requirement_price.split(', ') if self.requirement_price else []
        
        for price in prices:
            try:
                total += float(price.strip())
            except (ValueError, TypeError):
                pass
        
        return total
    
    def get_skill_level_display(self, level):
        """Возвращает отображаемое название уровня"""
        level_names = {
            'expert': 'Эксперт',
            'senior': 'Senior',
            'middle': 'Middle',
            'junior': 'Junior',
            'beginner': 'Начинающий',
            'unspecified': 'Уровень не указан'
        }
        return level_names.get(level, 'Уровень не указан')
