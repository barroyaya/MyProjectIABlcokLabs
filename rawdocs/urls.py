from django.urls import path
from . import views

app_name = 'rawdocs'
urlpatterns = [
    path('', views.upload_pdf, name='upload'),
    path('success/<int:pk>/', views.success, name='success'),
]
