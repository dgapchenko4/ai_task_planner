from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    ChangePasswordSerializer,
    NotificationSettingsSerializer
)

User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        # Приветственное письмо
        self.send_welcome_email(user)

        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'Регистрация успешна!'
        }, status=status.HTTP_201_CREATED)

    def send_welcome_email(self, user):
        """Приветственное письмо при регистрации"""
        if not settings.EMAIL_HOST_USER or settings.EMAIL_HOST_USER == 'your-email@gmail.com':
            return

        try:
            send_mail(
                subject='Добро пожаловать в AI Task Planner!',
                message=f'''Здравствуйте, {user.first_name}!

Вы успешно зарегистрировались в AI Task Planner — умном планировщике задач с искусственным интеллектом.

Возможности:
📝 Создание задач с AI-анализом
📅 Календарь с приоритетами
🏷 Автоматические теги
📧 Уведомления о задачах
⏰ Утренняя сводка задач

Настройте уведомления в профиле.

Войти: http://localhost:3000

С уважением,
AI Task Planner''',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Welcome email error: {e}")


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class NotificationSettingsView(APIView):
    """Настройки уведомлений"""
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        serializer = NotificationSettingsSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = NotificationSettingsSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Настройки сохранены', 'data': serializer.data})
        return Response(serializer.errors, status=400)


class ChangePasswordView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'Пароль изменен'})
        return Response(serializer.errors, status=400)
