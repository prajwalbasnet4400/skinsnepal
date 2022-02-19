from .models import Profile
import social_core.pipeline.social_auth

def save_profile(backend, user, response, *args, **kwargs):
    if backend.name == 'steam':
        profile = user.get_profile()
        if profile is None:
            profile = Profile(user_id=user.id)
        player_details = kwargs.get('details')
        extra_data = player_details.get('player')
        
        profile.avatar = extra_data.get('avatarfull')
        profile.save()