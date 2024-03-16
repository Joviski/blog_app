from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import Post
from .serializers import PostSerializer


class PostViewSet(viewsets.ModelViewSet):
    """Post Model ViewSet."""
    serializer_class = PostSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Override get_queryset method."""
        user = self.request.user
        return Post.objects.filter(author=user)

    def perform_create(self, serializer):
        """Override perform_create method."""
        serializer.save(author=self.request.user)