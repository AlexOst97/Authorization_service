from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True,
                              blank=True,
                              null=True,
                              verbose_name="Электронная почта")

    first_name = models.CharField(blank=True,
                                  null=True,
                                  max_length=50,
                                  verbose_name="Имя")

    last_name = models.CharField(blank=True,
                                 null=True,
                                 max_length=50,
                                 verbose_name="Фамилия")

    phone_number = models.CharField(max_length=15,
                                    unique=True,
                                    verbose_name="Номер телефона")

    city = models.CharField(max_length=50,
                            blank=True,
                            null=True,
                            verbose_name="Город")

    avatar = models.ImageField(upload_to="users/image",
                               blank=True,
                               null=True,
                               verbose_name="Изображение")

    is_active = models.BooleanField(default=True,
                                    verbose_name="Активный пользователь")

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.id} {self.first_name} {self.last_name}"