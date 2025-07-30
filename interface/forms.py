from users.models import User
from django import forms


class UserCreateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ("phone_number",)


class UserСheckForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ("phone_number", "authorization_code")


class ProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = "__all__"
        read_only_fields = (
            "is_active",
            "authorization_code",
        )
        extra_kwargs = {
            "phone_number": {"read_only": True},
            "invite_code": {"read_only": True},
        }
