from rest_framework import status
from django.http import FileResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from services.serializers.watermark_pdf_serializers import WatermarkPDFSerializer
from services.utils.services.watermark import apply_watermark
from drf_spectacular.utils import extend_schema


@extend_schema(tags=["PDF Watermarking"], request=WatermarkPDFSerializer)
class WatermarkPDFView(APIView):

    def post(self, request):
        serializer = WatermarkPDFSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        pdf_file = data["file"]
        text = data["text"]
        position = data["position"]
        opacity = data["opacity"]
        color = data["color"]

        try:
            watermarked_pdf = apply_watermark(
                pdf_file=pdf_file,
                text=text,
                position=position,
                opacity=opacity,
                color_hex=color
            )

            return FileResponse(
                watermarked_pdf,
                as_attachment=True,
                filename="watermarked.pdf",
                content_type="application/pdf",
            )

        except Exception as e:
            return Response(
                {
                    "error": (
                        "PDF watermarking failed",
                        str(e)
                    )
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )