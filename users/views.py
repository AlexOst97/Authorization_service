from rest_framework import generics
from users.models import User
from users.serializers import UserSerializers


class UserCreateAPIView(generics.CreateAPIView):
    serializer_class = UserSerializers
    queryset = User.objects.all()

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        user.set_password(user.password)
        user.save()


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