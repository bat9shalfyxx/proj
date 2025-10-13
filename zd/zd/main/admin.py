# main/admin.py
from django.contrib import admin
from .models import Application

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'id', 
        'organization_name', 
        'contact_email', 
        'contact_phone', 
        'status', 
        'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = [
        'organization_name', 
        'contact_email', 
        'contact_phone',
        'organization_inn'
    ]
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 20
    
    fieldsets = (
        ('Организация', {
            'fields': (
                'organization_name', 
                'organization_inn', 
                'organization_website'
            )
        }),
        ('Предлагаемое решение', {
            'fields': (
                'solution_name', 
                'solution_description', 
                'solution_experience'
            )
        }),
        ('Контактная информация', {
            'fields': (
                'contact_first_name',
                'contact_last_name', 
                'contact_middle_name',
                'contact_phone', 
                'contact_email'
            )
        }),
        ('Системная информация', {
            'fields': (
                'user',
                'status', 
                'created_at', 
                'updated_at'
            )
        }),
    )