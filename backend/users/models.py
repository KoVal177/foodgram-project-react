from django.contrib.auth.models import (AbstractBaseUser,
                                        BaseUserManager,
                                        PermissionsMixin,
                                        UserManager)
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_superuser(self,
                         username,
                         email,
                         first_name,
                         last_name,
                         password,
                         **other_fields):
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_active', True)

        if not other_fields.get('is_superuser'):
            raise ValueError('Недостаточно прав')

        if not other_fields.get('is_staff'):
            raise ValueError('Недостаточно прав')

        return self.create_user(email, username, first_name, last_name,
                                password, **other_fields)

    def create_user(self,
                    username,
                    first_name,
                    last_name,
                    email,
                    password,
                    **other_fields):
        if not email:
            raise ValueError('Наличие email обязательно')

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            **other_fields
        )
        user.set_password(password)
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        'Имя пользователя',
        max_length=100,
        unique=True,
    )
    email = models.EmailField(
        'E-mail',
        max_length=100,
        unique=True,
    )
    first_name = models.CharField(
        'Имя',
        max_length=100,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=100,
    )
    is_acitve = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    def has_permission(self, permission, obj=None) -> bool:
        return bool(self.is_superuser)

    def has_module_permission(self, app_label) -> bool:
        return bool(self.is_superuser)

    def get_fullname(self) -> str:
        return '{} {}'.format(self.first_name, self.last_name)

    def get_short_name(self) -> str:
        return str(self.username)

    def __str__(self) -> str:
        return str(self.email)


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='followed',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique follow'
            ),
        ]
