from rest_framework import status
from django.http import FileResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from services.serializers import TranslatePDFSerializer
from services.utils.services.pdf_reader import extract_text
from services.utils.services.translator import translate_pages
from services.utils.services.pdf_generator import generate_pdf
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample



@extend_schema(tags=["PDF Language Translation"], request=TranslatePDFSerializer)
class TranslatePDFView(APIView):

    def post(self, request):

        serializer = TranslatePDFSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        pdf_file = data["file"]

        source_language = (
            data["source_language"]
        )

        target_language = (
            data["target_language"]
        )

        try:

            # Extract PDF text
            pages = extract_text(pdf_file)

            # Translate the extracted text
            translated_pages = translate_pages(
                pages=pages,
                source_language=source_language,
                target_language=target_language,
            )

            # Generate new PDF
            translated_pdf = generate_pdf(
                translated_pages
            )

            return FileResponse(
                translated_pdf,
                as_attachment=True,
                filename="translated.pdf",
                content_type="application/pdf",
            )

        except Exception as e:

            return Response(
                {
                    "error": (
                        "PDF translation failed",
                        str(e)
                    )
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )