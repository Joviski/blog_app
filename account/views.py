from django.db import DatabaseError
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import UserSerializer, LoginSerializer
from .models import CustomUser


class UserViewSet(viewsets.ModelViewSet):
    """User Viewset."""
    serializer_class = UserSerializer
    http_method_names = ['get', 'post', 'put']
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def initialize_request(self, request, *args, **kwargs):
        self.action = self.action_map.get(request.method.lower())
        return super().initialize_request(request, *args, **kwargs)

    def get_authenticators(self):
        """Override get_authenticators method."""
        authentication_classes = self.authentication_classes
        if self.action in ['create', 'login']:
            authentication_classes = []
        return [auth() for auth in self.authentication_classes]

    def get_permissions(self):
        """Override get_permissions method."""
        permission_classes = self.permission_classes
        if self.action in ['create', 'login']:
            permission_classes = []
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """Override get_queryset method."""
        if self.request.user.is_superuser:
            return CustomUser.objects.all()
        return CustomUser.objects.filter(id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        """Override create method."""

        # This try block is to handle database error handling uniqueness 'probably a djongo issue.'
        try:
            return super().create(request, *args, **kwargs)
        except DatabaseError as e:
            return Response({
                    "detail": str(e) or "Something went wrong.",
                }, status=status.HTTP_400_BAD_REQUEST
            )

    @action(methods=["POST"], detail=False, url_path="login")
    def login(self, request):
        """Login endpoint."""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get("username")
        password = serializer.validated_data.get("password")
        user = CustomUser.objects.filter(username=username).first()
        if not user or not user.check_password(password):
            return Response({"error": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)

        token = Token.objects.get_or_create(user=user)[0]
        return Response(
            {"message": "User logged in.", "token": token.key}, status=status.HTTP_200_OK
        )

    @action(
        methods=["POST"],
        detail=False,
        url_path="logout",
        authentication_classes=[TokenAuthentication],
        permission_classes=[IsAuthenticated]
    )
    def logout(self, request):
        """Login endpoint."""
        user = request.user
        user.auth_token.delete()
        return Response(
            {"error": "User logged out"}, status=status.HTTP_200_OK
        )

