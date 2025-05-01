from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('new/', views.new_id_card, name='new_id_card'),
    path('view/', views.view_all, name='view_all'),
    path('edit/<int:student_id>/', views.edit_id_card, name='edit_id_card'),
    path('delete/<int:student_id>/', views.delete_id_card, name='delete_id_card'),
    path('download-id-card/', views.download_id_card, name='download_id_card'),
]
