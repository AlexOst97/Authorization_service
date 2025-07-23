from smsaero import SmsAero
from rest_framework import generics, status
from config.settings import SMSAERO_EMAIL, SMSAERO_API_KEY
from users.models import User
from users.serializers import UserCreateSerializers, UserСheckSerializers, ProfileSerializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
import random
import time
from users.services import generate_invite_code
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken


class UserCreateAPIView(generics.CreateAPIView):
    serializer_class = UserCreateSerializers
    queryset = User.objects.all()
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        user.set_unusable_password()
        user.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data['phone_number']
        phone_number_int = int(phone_number)

        user, created = User.objects.get_or_create(
            phone_number=phone_number,
            defaults={'is_active': True}
        )

        authorization_code = str(random.randint(1000, 9999))
        user.authorization_code = authorization_code
        user.save()

        try:
            print(authorization_code)
            # sms = SmsAero(email=SMSAERO_EMAIL, api_key=SMSAERO_API_KEY)
            # time.sleep(3)
            # sms.send_sms(phone_number_int,f'Ваш код подтверждения: {authorization_code}')

        except Exception as e:
            return Response(
                {"detail": "Не удалось отправить SMS", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {
                "detail": f"Код подтверждения отправлен на номер {user.phone_number}"
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )


class UserСheckAPIView(APIView):
    serializer_class = UserСheckSerializers
    queryset = User.objects.all()
    permission_classes = [AllowAny]

    def post(self, request):
        phone_number = request.data.get('phone_number')
        authorization_code = request.data.get('authorization_code')

        if not phone_number or not authorization_code:
            return Response(
                {"detail": "Необходимо указать номер телефона и код подтверждения"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return Response(
                {"detail": "Пользователь не найден"},
                status=status.HTTP_404_NOT_FOUND
            )

        if user.authorization_code != authorization_code:
            return Response(
                {"detail": "Неверный код подтверждения"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if 'invite_code' in request.data:
            user.invite_code = request.data['invite_code']
        elif not user.invite_code:
            user.invite_code = generate_invite_code()
        user.save()

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "detail": f"Успешная авторизация номера {user.phone_number}",
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_200_OK
        )


class ProfileAPIView(APIView):
    serializer_class = ProfileSerializers
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = self.serializer_class(user)

        related_users = User.objects.filter(vicarious_invite_code=user.invite_code)
        related_phones = [user.phone_number for user in related_users]
        response_data = serializer.data
        response_data['related_users'] = related_phones
        return Response(response_data)

    def post(self, request):
        user = request.user
        vicarious_invite_code = request.data.get('vicarious_invite_code')

        if not vicarious_invite_code:
            return Response(
                {"detail": "Необходимо указать инвайт-код"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.vicarious_invite_code:
            return Response(
                {"detail": "Вы уже активировали инвайт-код"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not User.objects.filter(invite_code=vicarious_invite_code).exists():
            return Response(
                {"detail": "Указанный инвайт-код не существует"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if vicarious_invite_code == user.invite_code:
            return Response(
                {"detail": "Нельзя использовать собственный инвайт-код"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.vicarious_invite_code = vicarious_invite_code
        user.save()

        return Response(
            {"detail": "Инвайт-код успешно активирован"},
            status=status.HTTP_200_OK
        )