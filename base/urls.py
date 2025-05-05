from django.urls import path
from . import views

urlpatterns = [
    path('image_upload/', views.image_upload_view, name='trigger-task'),
    path('image_list/<int:image_id>/', views.image_list_view, name='image-list')
]
