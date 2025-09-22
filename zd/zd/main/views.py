from django.shortcuts import render

def index(request):
    data = {
        'title': 'Главная страница',
    }
    return render(request, 'main/index.html', data)

def hub(request):
    data = {
        'title': 'Хаб',
    }
    return render(request, 'main/hubPage.html', data)

def profile(request):  # Добавьте эту функцию
    data = {
        'title': 'Профиль',
    }
    return render(request, 'main/profilePage.html', data)