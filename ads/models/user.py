from django.contrib.auth.models import AbstractUser
from ads.helpers.lazysignup_utils import is_lazy_user


class User(AbstractUser):

    @property
    def is_authenticated(self):
        try:
            if is_lazy_user(self):
                return False
        except:
            pass
        return True

    @property
    def is_anonymous(self):
        # # Check the user backend. If the lazy signup backend
        # # authenticated them, then the user is lazy.
        # backend = getattr(self, 'backend', None)
        # if backend == 'lazysignup.backends.LazySignupBackend':
        #     return True
        #
        # # Otherwise, we have to fall back to checking the database.
        # from lazysignup.models import LazyUser
        # return bool(LazyUser.objects.filter(user=self).count() > 0)
        return False

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'