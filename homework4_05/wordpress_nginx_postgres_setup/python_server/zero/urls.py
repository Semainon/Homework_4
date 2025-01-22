
from django.urls import path
from . import views

urlpatterns = [
    path('myWebBack', views.about, name='about'),  # Страница "О нас" по /api/about/
]
