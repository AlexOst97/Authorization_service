from users.apps import UsersConfig
from django.urls import path
from users.views import UserCreateAPIView, UserСheckAPIView, ProfileAPIView


app_name = UsersConfig.name

urlpatterns = [
    path("api_register/", UserCreateAPIView.as_view(), name="api-register"),
    path("api_register/check/", UserСheckAPIView.as_view(), name="api-register-check"),
    path("api_profile/", ProfileAPIView.as_view(), name="api-profile"),
]
