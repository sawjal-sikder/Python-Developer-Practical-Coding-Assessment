from django.urls import path
from services.views.translate_pdf_views import TranslatePDFView
from services.views.watermark_pdf_views import WatermarkPDFView

urlpatterns = [
    path("translate-pdf/", TranslatePDFView.as_view(), name="translate_pdf"),
    path("editor/pdf/watermark/", WatermarkPDFView.as_view(), name="watermark_pdf"),
]