from django.urls import path
from services.views import TranslatePDFView

urlpatterns = [
    path("translate-pdf/", TranslatePDFView.as_view(), name="translate_pdf"),       
]