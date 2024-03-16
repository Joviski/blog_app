from django.contrib.auth import password_validation, hashers

from rest_framework import serializers, exceptions
from account.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    """User serializer."""

    class Meta:
        """Meta class."""
        model = CustomUser
        fields = "__all__"
        extra_kwargs = {
            "password": {
                "write_only": True
            }
        }

    def validate_password(self, value):
        """Validate password."""
        password_validation.validate_password(value)
        return hashers.make_password(value)

    def validate_email(self, value):
        """Validate email."""
        if value and CustomUser.objects.filter(email=value).exists():
            raise exceptions.ValidationError(
                {"message": "Email already taken."}
            )
        return value


class LoginSerializer(serializers.Serializer):
    """Login serializer."""
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)