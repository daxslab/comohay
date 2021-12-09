import hashlib

from rest_framework import serializers, exceptions
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate

from ads.models import User


class LazyLoginSerializer(serializers.Serializer):
    usercode = serializers.CharField(required=True, allow_blank=False)

    def authenticate(self, username):
        user = User.objects.select_related('lazyuser').filter(username=username).first()

        if user and not hasattr(user, 'lazyuser'):
            msg = _('Unable to log in with provided credentials.')
            raise exceptions.ValidationError(msg)

        if not user:
            from lazysignup.models import LazyUser
            user, disposable_username = LazyUser.objects.create_lazy_user()
            user.username = username
            user.save()
        return authenticate(self.context['request'], username=username)

    def validate(self, attrs):
        usercode = attrs.get('usercode')
        username = hashlib.sha1(usercode.encode('utf-8')).hexdigest() if usercode else ''

        user = self.authenticate(username)

        # Did we get back an active user?
        if user:
            if not user.is_active:
                msg = _('User account is disabled.')
                raise exceptions.ValidationError(msg)
        else:
            msg = _('Unable to log in with provided credentials.')
            raise exceptions.ValidationError(msg)

        attrs['user'] = user
        return attrs