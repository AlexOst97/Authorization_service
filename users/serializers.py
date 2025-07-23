from rest_framework import serializers
from .models import User


class UserCreateSerializers(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("phone_number",)


class UserСheckSerializers(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("phone_number", "authorization_code")


class ProfileSerializers(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = "__all__"
        read_only_fields = ("is_active", "authorization_code",)
        extra_kwargs = {
            "phone_number": {'read_only': True},
            "invite_code": {'read_only': True},
        }