from rest_framework import serializers


class TranslatePDFSerializer(serializers.Serializer):

    file = serializers.FileField()
    source_language = serializers.CharField(max_length=20)
    target_language = serializers.CharField(max_length=20)

    def validate_file(self, value):

        if value.size == 0:
            raise serializers.ValidationError(
                "The uploaded file is empty."
            )

        if not value.name.lower().endswith(".pdf"):
            raise serializers.ValidationError(
                "Only PDF files are supported."
            )

        return value

    def validate(self, attrs):

        source = (
            attrs["source_language"]
            .strip()
            .lower()
        )

        target = (
            attrs["target_language"]
            .strip()
            .lower()
        )

        if source == target:
            raise serializers.ValidationError(
                "Source and target languages "
                "must be different."
            )

        attrs["source_language"] = source
        attrs["target_language"] = target

        return attrs