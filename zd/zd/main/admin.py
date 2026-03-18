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
        'contact_first_name',
        'contact_last_name',
        'team_role',
        'belbin_role',
        'expected_salary',
        'status',
        'created_at'
    ]

    list_filter = [
        'status',
        'team_role',
        'belbin_role',
        'activity_area',
        'it_skill',
        'work_schedule',
        'created_at'
    ]

    search_fields = [
        'contact_first_name',
        'contact_last_name',
        'contact_email',
        'technologies_text',      # или technologies_json, если нужно
        'project_examples',
        'work_experience',
        'collaboration_expectations'
    ]

    readonly_fields = ['created_at', 'updated_at']

    fieldsets = [
        ('Статус', {
            'fields': ['user', 'status']
        }),
        ('Область деятельности', {
            'fields': ['activity_area', 'activity_area_other']
        }),
        ('Ключевые навыки в IT', {
            'fields': ['it_skill', 'it_skill_other']
        }),
        ('Знание технологий', {
            'fields': ['technologies_json', 'technologies_text']  # подставьте свои поля
        }),
        ('Роль в команде (по Белбину)', {
            'fields': ['belbin_role']
        }),
        ('Ваша специальность', {
            'fields': ['team_role', 'team_role_other']
        }),
        ('Дополнительные сведения', {
            'fields': [
                'leaderid_link',
                'elibrary_link',
                'github_link',
                'project_examples',
                'work_experience',
                'driver_license'
            ]
        }),
        ('Ожидаемое вознаграждение и требования', {
            'fields': [
                'expected_salary',
                'work_schedule',
                'work_schedule_other',
                'required_equipment'
            ]
        }),
        ('Ожидание от сотрудничества', {
            'fields': ['collaboration_expectations']
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