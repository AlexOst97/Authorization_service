from django.contrib.auth.views import LogoutView

from interface.apps import InterfaceConfig
from django.urls import path
from interface.views import UserCreateView, UserСheckView, ProfileView, UserDetailView, UserUpdateView


app_name = InterfaceConfig.name

urlpatterns = [
    path("register/", UserCreateView.as_view(), name="register"),
    path("register/check/", UserСheckView.as_view(), name="check"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("detail/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("update/<int:pk>/", UserUpdateView.as_view(), name="user-update"),
    path("logout/", LogoutView.as_view(next_page="users:login"), name="logout"),
]