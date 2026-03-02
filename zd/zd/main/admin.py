from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django import forms
from .models import CustomUser
from .models_application import Application
    
class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomUser

class CustomUserCreationFormAdmin(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name')


from django.contrib import admin
from .models import CustomUser, Application
from .models_application import Application

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'id', 
        'organization_name', 
        'contact_first_name', 
        'contact_last_name',
        'team_role',  # Вместо solution_name
        'age',        # Новое поле
        'status', 
        'created_at'
    ]
    
    list_filter = ['status', 'team_role', 'created_at']
    search_fields = [
        'organization_name', 
        'contact_first_name', 
        'contact_last_name', 
        'contact_email',
        'about_me'  # Новое поле для поиска
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = [
        ('Основная информация', {
            'fields': [
                'user', 
                'status', 
                'team_role',  # Вместо solution_name
                'age',        # Новое поле
                'about_me'     # Новое поле
            ]
        }),
        ('Навыки', {
            'fields': ['skill_list', 'skills_json']
        }),
        ('Организация', {
            'fields': [
                'organization_name', 
                'organization_inn', 
                'organization_website'
            ]
        }),
        ('Контакты', {
            'fields': [
                'contact_first_name', 
                'contact_last_name', 
                'contact_middle_name',
                'contact_phone', 
                'contact_email'
            ]
        }),
        ('Ресурсы', {
            'fields': ['requirement_name', 'requirement_price']
        }),
        ('Системная информация', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    
    actions = ['approve_applications', 'reject_applications']
    
    def approve_applications(self, request, queryset):
        queryset.update(status='approved')
        self.message_user(request, f"{queryset.count()} заявок одобрено")
    approve_applications.short_description = "Одобрить выбранные заявки"
    
    def reject_applications(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, f"{queryset.count()} заявок отклонено")
    reject_applications.short_description = "Отклонить выбранные заявки"


class CustomUserAdmin(admin.ModelAdmin):
    list_display = [
        'username', 
        'email', 
        'phone_number', 
        'first_name', 
        'last_name', 
        'is_active',
        'is_staff'
    ]
    
    list_filter = ['is_active', 'is_staff', 'is_superuser']
    
    search_fields = [
        'username', 
        'email', 
        'phone_number', 
        'first_name', 
        'last_name'
    ]
    
    fieldsets = [
        ('Основная информация', {
            'fields': [
                'username', 
                'email', 
                'phone_number',
                'first_name', 
                'last_name', 
                'middle_name'
            ]
        }),
        ('Права доступа', {
            'fields': [
                'is_active', 
                'is_staff', 
                'is_superuser',
                'groups', 
                'user_permissions'
            ]
        }),
        ('Важные даты', {
            'fields': ['last_login', 'date_joined'],
            'classes': ['collapse']
        }),
    ]

admin.site.register(CustomUser, CustomUserAdmin)