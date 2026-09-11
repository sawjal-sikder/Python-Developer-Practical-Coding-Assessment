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


class WatermarkPDFSerializer(serializers.Serializer):
    file = serializers.FileField()
    text = serializers.CharField(max_length=200)
    position = serializers.CharField(max_length=20)
    opacity = serializers.FloatField()
    color = serializers.CharField(max_length=10)

    def validate_file(self, value):
        if value.size == 0:
            raise serializers.ValidationError("The uploaded file is empty.")
        if not value.name.lower().endswith(".pdf"):
            raise serializers.ValidationError("Only PDF files are supported.")
        return value

    def validate_position(self, value):
        val = value.strip().lower()
        valid_positions = [
            "top-left", "top-center", "top-right",
            "center",
            "bottom-left", "bottom-center", "bottom-right"
        ]
        if val not in valid_positions:
            raise serializers.ValidationError(
                f"Invalid position. Must be one of: {', '.join(valid_positions)}"
            )
        return val

    def validate_opacity(self, value):
        if not (0.0 <= value <= 1.0):
            raise serializers.ValidationError("Opacity must be between 0.0 and 1.0.")
        return value

    def validate_color(self, value):
        val = value.strip()
        # Regex to validate hex color code (with or without # prefix, 3 or 6 chars)
        import re
        if not re.match(r"^#?[0-9a-fA-F]{3}$|^#?[0-9a-fA-F]{6}$", val):
            raise serializers.ValidationError("Color must be a valid hex color code, e.g., #FF0000.")
        return val