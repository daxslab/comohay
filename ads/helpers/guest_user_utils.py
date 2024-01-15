def is_guest_user(user):
    """ Return True if the passed user is a lazy user. """
    # Check the user backend. If the lazy signup backend
    # authenticated them, then the user is lazy.
    backend = getattr(user, 'backend', None)
    if backend == 'guest_user.backends.GuestBackend':
        return True

    # Otherwise, we have to fall back to checking the database.
    from guest_user.models import Guest
    return bool(Guest.objects.filter(user=user).count() > 0)
