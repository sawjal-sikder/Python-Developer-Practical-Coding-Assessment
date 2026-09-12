import re
from rest_framework import serializers


class WatermarkPDFSerializer(serializers.Serializer):
    
    POSITION_CHOICES = [
        ("top-left", "Top Left"),
        ("top-center", "Top Center"),
        ("top-right", "Top Right"),
        ("center", "Center"),
        ("bottom-left", "Bottom Left"),
        ("bottom-center", "Bottom Center"),
        ("bottom-right", "Bottom Right"),
    ]
    
    OPACITY_CHOICES = [
        (0.25, "25%"),
        (0.50, "50%"),
        (0.75, "75%"),
        (1.0, "100%"),
    ]
    
    COLOR_CHOICES = [
        ("#000000", "Black"),
        ("#FFFFFF", "White"),
        ("#FF0000", "Red"),
        ("#00FF00", "Green"),
        ("#0000FF", "Blue"),
        ("#FFFF00", "Yellow"),
        ("#FFA500", "Orange"),
        ("#800080", "Purple"),
        ("#00FFFF", "Cyan"),
    ]
    
    file = serializers.FileField()
    text = serializers.CharField(max_length=200)
    position = serializers.ChoiceField(choices=POSITION_CHOICES)
    opacity = serializers.ChoiceField(choices=OPACITY_CHOICES)
    color = serializers.ChoiceField(choices=COLOR_CHOICES)

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
        if not re.match(r"^#?[0-9a-fA-F]{3}$|^#?[0-9a-fA-F]{6}$", val):
            raise serializers.ValidationError("Color must be a valid hex color code, e.g., #FF0000.")
        return val