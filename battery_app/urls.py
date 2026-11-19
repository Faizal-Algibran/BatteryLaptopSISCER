from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('add/', views.add_record_view, name='add_record'),
    path('delete/<int:pk>/', views.delete_record_view, name='delete_record'),
    path('api/chat/', views.chatbot_api, name='chatbot_api'),
]