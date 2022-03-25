from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


class EmailOrUsernameModelBackend(ModelBackend):
    """
    Authentication backend which allows users to authenticate using either their
    username or email address

    Source: https://stackoverflow.com/a/35836674/59984
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        user_model = get_user_model()

        if username is None:
            username = kwargs.get(user_model.USERNAME_FIELD)

        users = user_model._default_manager.filter(
            Q(**{user_model.USERNAME_FIELD: username}) | Q(**{user_model.EMAIL_FIELD: username})
        )

        for user in users:
            if user.check_password(password):
                return user
        return super().authenticate(request, username=None, password=None, **kwargs)
