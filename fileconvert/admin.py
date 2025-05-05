from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import DocumentFile
from .tasks import document_convert

class DocumentFileAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'get_original_filename',
        'conversion_type',
        'status',
        'uploaded_at',
        'get_converted_filename',
        'original_size',
        'converted_size',
        'error_message',
    )
    list_filter = ('status', 'conversion_type')
    search_fields = ('id__string', 'error_message', 'status')
    ordering = ('-uploaded_at',)
    readonly_fields = (
        'id',
        'uploaded_at',
        'converted_file',
        'status',
        'error_message',
        'original_size',
        'converted_size',
    )
    actions = ['retry_failed_conversions']

    def get_original_filename(self, obj):
        """Display original file name with a link to download."""
        if obj.original_file:
            url = obj.original_file.url
            return format_html('<a href="{}">{}</a>', url, obj.original_file.name.split('/')[-1])
        return "-"
    get_original_filename.short_description = 'Original File'

    def get_converted_filename(self, obj):
        """Display converted file name with a link to download."""
        if obj.converted_file:
            url = obj.converted_file.url
            return format_html('<a href="{}">{}</a>', url, obj.converted_file.name.split('/')[-1])
        return "-"
    get_converted_filename.short_description = 'Converted File'

    def retry_failed_conversions(self, request, queryset):
        """Retry conversion for failed documents."""
        failed_docs = queryset.filter(status='failed')
        for doc in failed_docs:
            doc.status = 'pending'
            doc.error_message = None
            doc.save()
            document_convert.delay(str(doc.id))
        self.message_user(request, f"Retried {failed_docs.count()} failed conversions.")
    retry_failed_conversions.short_description = "Retry failed conversions"

admin.site.register(DocumentFile, DocumentFileAdmin)