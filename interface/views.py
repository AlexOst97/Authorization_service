import time
from django.urls import reverse_lazy, reverse
from django.views.generic import View, DetailView, UpdateView
from smsaero import SmsAero
from config.settings import SMSAERO_EMAIL, SMSAERO_API_KEY
from interface.forms import UserCreateForm, UserСheckForm, ProfileForm
import random
from users.services import generate_invite_code
from django.contrib import messages
from django.shortcuts import render, redirect
from users.models import User
from django.contrib.auth import login


class UserCreateView(View):
    model = User
    form_class = UserCreateForm
    template_name = "user_create.html"
    success_url = reverse_lazy("interface:check")

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        phone_number = request.POST.get("phone_number")
        if not phone_number:
            messages.error(request, "Необходимо указать номер телефона")
            return render(request, self.template_name)

        user, created = User.objects.get_or_create(
            phone_number=phone_number, defaults={"is_active": True}
        )

        authorization_code = str(random.randint(1000, 9999))
        user.authorization_code = authorization_code
        user.save()

        try:
            # print(f"Код подтверждения: {authorization_code}")
            sms = SmsAero(email=SMSAERO_EMAIL, api_key=SMSAERO_API_KEY)
            time.sleep(3)
            sms.send_sms(int(phone_number), f'Ваш код подтверждения: {authorization_code}')
            messages.success(
                request, f"Код подтверждения отправлен на номер {phone_number}"
            )
        except Exception as e:
            messages.error(request, f"Не удалось отправить SMS: {str(e)}")

        return redirect(self.success_url)


class UserСheckView(View):
    model = User
    form_class = UserСheckForm
    template_name = "user_check.html"
    success_url = reverse_lazy("interface:profile")

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        phone_number = request.POST.get("phone_number")
        authorization_code = request.POST.get("authorization_code")
        invite_code = request.POST.get("invite_code")

        if not phone_number or not authorization_code:
            messages.error(
                request, "Необходимо указать номер телефона и код подтверждения"
            )
            return render(request, self.template_name)
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            messages.error(request, "Пользователь не найден")
            return render(request, self.template_name)

        if user.authorization_code != authorization_code:
            messages.error(request, "Неверный код подтверждения")
            return render(request, self.template_name)

        login(request, user)

        if invite_code and not user.invite_code:
            user.invite_code = invite_code
        elif not user.invite_code:
            user.invite_code = generate_invite_code()
        user.save()

        messages.success(request, f"Успешная авторизация номера {phone_number}")
        return redirect(self.success_url)


class ProfileView(View):
    model = User
    form_class = ProfileForm
    template_name = "profile.html"

    def get_success_url(self):
        return reverse("interface:user-detail", kwargs={"pk": self.request.user.pk})

    def get(self, request):
        user = request.user
        return render(request, self.template_name)

    def post(self, request):
        user = request.user
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        vicarious_invite_code = request.POST.get("vicarious_invite_code")

        if not vicarious_invite_code:
            messages.error(request, "Необходимо указать инвайт-код")
            return render(request, self.template_name)

        if user.vicarious_invite_code:
            messages.error(request, "Вы уже активировали инвайт-код")
            return render(request, self.template_name)

        if not User.objects.filter(invite_code=vicarious_invite_code).exists():
            messages.error(request, "Указанный инвайт-код не существует")
            return render(request, self.template_name)

        if vicarious_invite_code == user.invite_code:
            messages.error(request, "Нельзя использовать собственный инвайт-код")
            return render(request, self.template_name)

        user.first_name = first_name
        user.last_name = last_name
        user.vicarious_invite_code = vicarious_invite_code
        user.save()

        messages.success(request, "Данные успешно сохранены!")
        return redirect(self.get_success_url())


class UserDetailView(DetailView):
    model = User
    form_class = ProfileForm
    template_name = "user_detail.html"

    def get_change(self):
        return User.objects.filter(pk=self.request.user.pk)

    def get(self, request, *args, **kwargs):
        current_user = request.user
        user = self.get_object()
        related_users = User.objects.filter(
            vicarious_invite_code=current_user.invite_code
        ).exclude(id=current_user.id)

        context = {
            "user": user,
            "current_user": current_user,
            "related_users": related_users,
        }
        return render(request, self.template_name, context)


class UserUpdateView(UpdateView):
    model = User
    form_class = ProfileForm
    template_name = "user_update.html"

    def get_success_url(self):
        return reverse("interface:user-detail", kwargs={"pk": self.request.user.pk})

    def post(self, request, *args, **kwargs):

        user = request.user
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        city = request.POST.get("city")
        email = request.POST.get("email")
        password = request.POST.get("password")
        avatar = request.POST.get("avatar")

        user.first_name = first_name
        user.last_name = last_name
        user.city = city
        user.email = email
        user.password = password
        user.avatar = avatar
        user.save()

        messages.success(request, "Данные успешно обновлены!")
        return redirect(self.get_success_url())
