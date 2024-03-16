from rest_framework import serializers
from .models import Post


class PostSerializer(serializers.ModelSerializer):
    """Post serializer."""
    class Meta:
        """Meta Class."""
        model = Post
        fields = "__all__"
        read_only_fields = ["author"]
