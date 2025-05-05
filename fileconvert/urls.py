from django.urls import path
from .views import document_upload_view, document_download_view

urlpatterns = [
    path('document_upload/', document_upload_view, name='document_upload'),
    path('documents/<uuid:document_id>/', document_download_view, name='document_download'),
]