from rest_framework import serializers
from .models import User


class UserSerializers(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = "__all__"
        read_only_fields = ("is_active",)
        extra_kwargs = {"password": {'write_only': True}}