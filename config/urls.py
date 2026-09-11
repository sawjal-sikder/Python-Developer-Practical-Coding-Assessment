from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect as Redirect # type: ignore
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from services.views import WatermarkPDFView


def MainView(request):
    return Redirect('api/schema/swagger-ui/') 

urlpatterns = [
    path('', MainView),
    path('admin/', admin.site.urls),
    path('api/', include('services.urls')),
    path('editor/pdf/watermark/', WatermarkPDFView.as_view(), name='watermark_pdf'),
    
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc')
]
