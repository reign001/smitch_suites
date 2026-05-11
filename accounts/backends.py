from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q


class UsernameOrPhoneBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()

        print("BACKEND USER MODEL:", UserModel)
        print("BACKEND USERNAME:", username)
        print("BACKEND PASSWORD:", password)

        try:
            user = UserModel.objects.get(username=username)
            print("FOUND BY USERNAME:", user)
        except UserModel.DoesNotExist:
            print("NOT FOUND BY USERNAME")

            try:
                user = UserModel.objects.get(phone=username)
                print("FOUND BY PHONE:", user)
            except UserModel.DoesNotExist:
                print("NOT FOUND BY PHONE")
                return None

        print("USER IS ACTIVE:", user.is_active)
        print("PASSWORD CHECK:", user.check_password(password))

        if user.check_password(password) and user.is_active:
            return user

        return None