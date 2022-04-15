from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from django.db.models import signals
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from my_project.accounts.models import Profile, ContactForm


@receiver(signals.post_save, sender=get_user_model())
def create_profile_with_registration(instance, created, **kwargs):
    if not created:
        return None
    profile = Profile(user=instance)
    profile.save()


@receiver(signals.post_save, sender=get_user_model())
def create_contact_form_with_registration(instance, created, **kwargs):
    if not created:
        return None
    contact_form = ContactForm(user=instance)
    contact_form.save()


@receiver(signals.post_save, sender=SocialAccount)
def fill_profile_with_google_account(instance, created, **kwargs):
    if not created:
        return None

    social_account = instance
    first_name = social_account.extra_data.get('given_name')
    last_name = social_account.extra_data.get('family_name')
    profile_picture = social_account.extra_data.get('picture')
    nationality = 'Bulgarian' if social_account.extra_data.get('locale') == "bg" else ''
    profile = Profile(first_name=first_name,
                      last_name=last_name,
                      picture_url=profile_picture,
                      nationality=nationality,
                      user=social_account.user)
    profile.save()


def is_staff_automatically_set(sender, instance, **kwargs):
    if instance.groups.count() > 0:
        instance.is_staff = True
    else:
        instance.is_staff = False
    instance.save()


m2m_changed.connect(is_staff_automatically_set, sender=get_user_model().groups.through)
