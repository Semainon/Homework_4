from django.shortcuts import render

def about(request):
    return render(request, 'about.html')  # Шаблон для страницы "О нас"

