
# main/models_application.py
from django.db import models
from django.conf import settings

class Application(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'В обработке'),
        ('approved', 'Одобрена'),
        ('rejected', 'Отклонена'),
    ]
    
    def get_absolute_url(self):
        return f'/news/{self.id}'
    
    # Организация
    organization_name = models.CharField('Наименование организации', max_length=255)
    organization_inn = models.CharField('ИНН организации', max_length=12)
    organization_website = models.URLField('Сайт организации', blank=True)
    
    # Предлагаемое решение
    solution_name = models.CharField('Краткое наименование решения', max_length=255)
    solution_description = models.TextField('Описание предлагаемого решения')
    solution_experience = models.TextField('Релевантный опыт применения')
    
    # Контакты
    contact_first_name = models.CharField('Имя', max_length=100)
    contact_last_name = models.CharField('Фамилия', max_length=100)
    contact_middle_name = models.CharField('Отчество', max_length=100, blank=True)
    contact_phone = models.CharField('Телефон', max_length=20)
    contact_email = models.EmailField('Электронная почта')
    
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
        verbose_name='Пользователь'
    )
    
    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Заявка от {self.organization_name} ({self.created_at.strftime('%d.%m.%Y')})"