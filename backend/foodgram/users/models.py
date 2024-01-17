from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from users.validators import username_validator


class User(AbstractUser):
    """Класс пользователей."""
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=settings.LIMIT_USERNAME,
        unique=True,
        db_index=True,
        blank=False,
        validators=(username_validator,),
        error_messages={
            "unique": "Пользователь с таким именем уже существует!",
        },
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=settings.LIMIT_USERNAME,
        blank=False,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=settings.LIMIT_USERNAME,
        blank=False,
    )
    email = models.EmailField(
        verbose_name='Email',
        blank=False,
        unique=True,
        db_index=True,
        help_text='Введите свой электронный адрес',
        max_length=settings.LIMIT_EMAIL,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('-id',)
        constraints = (
            models.UniqueConstraint(
                fields=('username', 'email'),
                name='unique_username_email'
            ),
        )

    def __str__(self):
        return self.username
