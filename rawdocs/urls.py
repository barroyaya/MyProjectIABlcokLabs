# rawdocs/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'rawdocs'

urlpatterns = [
    # 1) Page d’accueil → login
    path(
        '',
        auth_views.LoginView.as_view(
            template_name='registration/login.html'
        ),
        name='login'
    ),

    # 2) Déconnexion
    path(
        'logout/',
        auth_views.LogoutView.as_view(next_page='rawdocs:login'),
        name='logout'
    ),

    # 3) Inscription
    path(
        'register/',
        views.register,
        name='register'
    ),

    # 4) Après authentification → upload
    path(
        'upload/',
        views.upload_pdf,
        name='upload'
    ),

]
