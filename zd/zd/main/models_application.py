# main/models_application.py
from django.db import models
from django.conf import settings
from django.core.validators import ValidationError
import json
from decimal import Decimal

class Application(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'В обработке'),
        ('approved', 'Одобрена'),
        ('rejected', 'Отклонена'),
    ]
    
    def get_absolute_url(self):
        return f'/news/{self.id}'
    
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
    
    team_role = models.CharField(
        'Роль в команде', 
        max_length=50, 
        choices=TEAM_ROLE_CHOICES, 
        default='developer',
        blank=True
    )
    
    # Навыки - текстовое поле для обратной совместимости
    skill_list = models.TextField('Ваши навыки', default='JS, REACT, TypeScript', blank=True)
    
    # Новое поле для хранения навыков в структурированном виде
    skills_json = models.JSONField('Навыки (структурированные)', default=list, blank=True)

    # Организация
    organization_name = models.CharField('Наименование организации', max_length=255, default='NewOrg')
    organization_inn = models.CharField('ИНН организации', max_length=12, default='1000000000')
    organization_website = models.URLField('Сайт организации', blank=True, default='http://NewOrg.com')
    
    # Предлагаемое решение
    solution_name = models.CharField('Краткое наименование решения', max_length=255, default='-')
    solution_description = models.TextField('Описание предлагаемого решения', default='-')
    solution_experience = models.TextField('Релевантный опыт применения', default='-')

    # Контакты
    contact_first_name = models.CharField('Имя', max_length=100, default='Тимур')
    contact_last_name = models.CharField('Фамилия', max_length=100, default='Шокиров')
    contact_middle_name = models.CharField('Отчество', max_length=100, blank=True)
    contact_phone = models.CharField('Телефон', max_length=20, default='+79879879292')
    contact_email = models.EmailField('Электронная почта', default='ya@gmail.com')
    
    # Системные поля
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    # РЕСУРС-ЦЕНА
    requirement_name = models.TextField('Название ресурса', max_length=255, default='Ноут')
    requirement_price = models.CharField('Цена ресурса', default=10000, max_length=255)
    
    # Связь с пользователем
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
        # Синхронизируем skill_list с skills_json для обратной совместимости
        if self.skills_json and not self.skill_list:
            skills_text = ', '.join([skill.get('name', '') for skill in self.skills_json if skill.get('name')])
            self.skill_list = skills_text
        elif self.skill_list and not self.skills_json:
            # Конвертируем старый формат в новый при необходимости
            try:
                # Проверяем, не является ли skill_list уже JSON строкой
                if self.skill_list.startswith('[') and self.skill_list.endswith(']'):
                    self.skills_json = json.loads(self.skill_list)
                else:
                    # Разделяем по запятой и создаем структуру
                    skills = [s.strip() for s in self.skill_list.split(',') if s.strip()]
                    self.skills_json = [{'name': skill, 'level': 'unspecified'} for skill in skills]
            except:
                # Если ошибка парсинга, оставляем как есть
                pass
                
        super().save(*args, **kwargs)
    
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
        
        if self.skills_json:
            for skill in self.skills_json:
                level = skill.get('level', 'unspecified')
                if level in skills_by_level:
                    skills_by_level[level].append(skill)
                else:
                    skills_by_level['unspecified'].append(skill)
        
        return skills_by_level
    
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