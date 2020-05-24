from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from lazysignup.models import LazyUser
from allauth.account.adapter import get_adapter as get_account_adapter


class SocialAccountAdapter(DefaultSocialAccountAdapter):

    def save_user(self, request, sociallogin, form=None):
        """
        Saves a newly signed up social login. In case of auto-signup,
        the signup form is not available.
        """
        u = sociallogin.user
        u.set_unusable_password()
        u.id = request.user.id
        get_account_adapter().populate_username(request, u)
        LazyUser.objects.filter(user=u).delete()
        sociallogin.save(request)
        return u
