from django.urls import path
from . import views

urlpatterns = [
    path('image_upload/', views.image_upload_view, name='trigger-task'),
]
