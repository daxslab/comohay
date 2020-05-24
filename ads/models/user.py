from django.contrib.auth.models import User, AbstractUser
from lazysignup.utils import is_lazy_user


class User(AbstractUser):

    @property
    def is_authenticated(self):
        try:
            if is_lazy_user(self):
                return False
        except:
            pass
        return True

    # @property
    # def is_anonymous(self):
    #     try:
    #         if is_lazy_user(self):
    #             return True
    #     except:
    #         pass
    #     return False

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'