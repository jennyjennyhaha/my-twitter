
def profile_changed(sender, instance, **kwargs):
    # import written in the func to avoid circle dependency
    from accounts.services import UserService
    UserService.invalidate_profile(instance.user_id)
