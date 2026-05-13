import os
import django
import json
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zd.settings')
django.setup()

from faker import Faker
from main.models import Project, ProjectRequirement
from main.models_application import Application
from django.contrib.auth import get_user_model

fake = Faker('ru_RU')
User = get_user_model()

STATUSES = ['new', 'in_progress', 'approved', 'rejected']
TEAM_ROLES = ['visionary', 'implementer', 'leader', 'organizer', 'analyst', 
              'communicator', 'perfectionist', 'resource_investigator', 
              'developer', 'designer', 'project_manager', 'other']
SKILL_LEVELS = ['expert', 'senior', 'middle', 'junior', 'beginner', 'unspecified']
SKILLS_LIST = [
    'Python', 'JavaScript', 'TypeScript', 'React', 'Django', 'Node.js',
    'HTML/CSS', 'SQL', 'Docker', 'Git', 'Java', 'C#', 'PHP', 'Vue.js',
    'Angular', 'PostgreSQL', 'MongoDB', 'REST API', 'GraphQL'
]

def create_test_user():
    """Создание тестового пользователя"""
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Тестовый',
            'last_name': 'Пользователь'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print('Создан тестовый пользователь')
    return user

def create_fake_projects(count=10):
    """Создание фейковых проектов"""
    user = create_test_user()
    
    statuses = ['draft', 'active', 'in_progress', 'completed', 'on_hold']
    
    for i in range(count):
        project = Project.objects.create(
            creator=user,
            name=fake.sentence(nb_words=4)[:-1],
            description=fake.paragraph(nb_sentences=3),
            team_activities=fake.text(max_nb_chars=100),
            work_conditions=fake.text(max_nb_chars=100),
            start_date=fake.date_between(start_date='-1y', end_date='today'),
            end_date=fake.date_between(start_date='today', end_date='+1y'),
            budget=random.randint(100000, 10000000),
            status=random.choice(statuses),
            keywords=', '.join(fake.words(nb=5))
        )
        
        # Добавляем требования к проекту
        for j in range(random.randint(1, 3)):
            ProjectRequirement.objects.create(
                project=project,
                skill_name=random.choice(SKILLS_LIST),
                level_requirement=random.choice(SKILL_LEVELS),
                people_count=random.randint(1, 5),
                is_mandatory=random.choice([True, False]),
                price=random.randint(50000, 500000)
            )
        
        print(f'Создан проект: {project.name}')
    
    print(f'✅ Создано {count} проектов')

def create_fake_applications(count=15):
    """Создание фейковых заявок"""
    user = create_test_user()
    
    org_names = [
        'ООО ТехноИнновации', 'ИП Цифровые Решения', 'ЗАО Альфа-Софт',
        'ООО Бизнес-Аналитика', 'ИП Веб-Студия', 'ООО АйТи Решения',
        'ООО Консалтинг Групп', 'ИП Разработчик'
    ]
    
    for i in range(count):
        # Генерируем навыки в JSON формате
        num_skills = random.randint(1, 5)
        skills_json = []
        for _ in range(num_skills):
            skills_json.append({
                'name': random.choice(SKILLS_LIST),
                'level': random.choice(SKILL_LEVELS)
            })
        
        # Текстовое представление навыков
        skill_list = ', '.join([s['name'] for s in skills_json])
        
        # Генерируем ресурсы
        num_resources = random.randint(0, 3)
        requirement_names = []
        requirement_prices = []
        for _ in range(num_resources):
            requirement_names.append(random.choice(['Ноутбук', 'Рабочая станция', 'Лицензия ПО', 'Обучение', 'Оборудование']))
            requirement_prices.append(str(random.randint(10000, 500000)))
        
        app = Application.objects.create(
            user=user if random.choice([True, False]) else None,
            status=random.choice(STATUSES),
            
            contact_last_name=fake.last_name(),
            contact_first_name=fake.first_name(),
            contact_middle_name=fake.middle_name() if random.choice([True, False]) else '',
            contact_phone=f'+7{random.randint(9000000000, 9999999999)}',
            contact_email=fake.email(),
            age=random.randint(18, 65) if random.choice([True, False]) else None,
            
            about_me=fake.paragraph(nb_sentences=3) if random.choice([True, False]) else '',
            
            team_role=random.choice(TEAM_ROLES) if random.choice([True, False]) else None,
            
            skill_list=skill_list,
            skills_json=skills_json,
            
            organization_name=random.choice(org_names),
            organization_inn=str(random.randint(1000000000, 999999999999)),
            organization_website=fake.url() if random.choice([True, False]) else '',
            
            requirement_name=', '.join(requirement_names) if requirement_names else '',
            requirement_price=', '.join(requirement_prices) if requirement_prices else ''
        )
        
        print(f'Создана заявка #{app.id}: {app.organization_name} ({app.contact_first_name} {app.contact_last_name})')
    
    print(f'✅ Создано {count} заявок')

def show_statistics():
    """Показать статистику после создания"""
    print("\n" + "="*50)
    print("📊 СТАТИСТИКА БАЗЫ ДАННЫХ")
    print("="*50)
    print(f"👤 Пользователей: {User.objects.count()}")
    print(f"📁 Проектов: {Project.objects.count()}")
    print(f"📋 Заявок: {Application.objects.count()}")
    
    if Project.objects.exists():
        print(f"\n📌 Примеры проектов:")
        for project in Project.objects.all()[:3]:
            print(f"   - {project.name} (Статус: {project.get_status_display()})")
    
    if Application.objects.exists():
        print(f"\n📌 Примеры заявок:")
        for app in Application.objects.all()[:3]:
            print(f"   - #{app.id}: {app.organization_name} ({app.contact_first_name} {app.contact_last_name})")

if __name__ == '__main__':
    print("="*50)
    print("🚀 НАЧАЛО СОЗДАНИЯ ФЕЙКОВЫХ ДАННЫХ")
    print("="*50)
    
    user = create_test_user()
    user.set_password('testpass123')
    user.save()
    
    print("\n📁 Создание проектов...")
    create_fake_projects(10)
    
    print("\n📋 Создание заявок...")
    create_fake_applications(15)
    
    show_statistics()
    
    print("\n" + "="*50)
    print("✅ ГОТОВО!")
    print("="*50)
    print("🔑 Данные для входа в систему:")
    print("   Логин: testuser")
    print("   Пароль: testpass123")
    print("="*50)