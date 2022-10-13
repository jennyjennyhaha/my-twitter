from accounts.listeners import profile_changed
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save, pre_delete
from utils.listeners import invalidate_object_cache


class UserProfile(models.Model):
    # One2One field creates a unique index to make sure there is no multiple UserProfile pointing to same User
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    # Django has an ImageField，better not use it
    avatar = models.FileField(null=True)
    # when user is created, an object called uer profile will be created
    # null=True
    nickname = models.CharField(null=True, max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} {}'.format(self.user, self.nickname)


# define property method，put it in User model
def get_profile(user):
    from accounts.services import UserService

    if hasattr(user, '_cached_user_profile'):
        return getattr(user, '_cached_user_profile')
    profile = UserService.get_profile_through_cache(user.id)
    # cache to avoid repeated queries
    setattr(user, '_cached_user_profile', profile)
    return profile


# add a 'profile' property method to User Model
User.profile = property(get_profile)

# hook up with listeners to invalidate cache
pre_delete.connect(invalidate_object_cache, sender=User)
post_save.connect(invalidate_object_cache, sender=User)

pre_delete.connect(profile_changed, sender=UserProfile)
post_save.connect(profile_changed, sender=UserProfile)
