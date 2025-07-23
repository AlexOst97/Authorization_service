from smsaero import SmsAero
from rest_framework import generics, status
from config.settings import SMSAERO_EMAIL, SMSAERO_API_KEY
from users.models import User
from users.serializers import UserSerializers, UserСheckSerializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import random
import time
from users.services import generate_invite_code
from rest_framework.views import APIView


class UserCreateAPIView(generics.CreateAPIView):
    serializer_class = UserSerializers
    queryset = User.objects.all()
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        user.set_password(user.password)
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
            sms = SmsAero(email=SMSAERO_EMAIL, api_key=SMSAERO_API_KEY)
            time.sleep(3)
            sms.send_sms(phone_number_int,f'Ваш код подтверждения: {authorization_code}')

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

        user.invite_code = generate_invite_code()
        user.save()

        return Response(
            {
                "detail": f"Успешная авторизация номера {user.phone_number}",
            },
            status=status.HTTP_200_OK
        )


class UserUpdateAPIView(generics.UpdateAPIView):
    serializer_class = UserSerializers
    queryset = User.objects.all()


class UserDestroyAPIView(generics.DestroyAPIView):
    serializer_class = UserSerializers
    queryset = User.objects.all()


class UserListAPIView(generics.ListAPIView):
    serializer_class = UserSerializers
    queryset = User.objects.all()


class UserRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = UserSerializers
    queryset = User.objects.all()