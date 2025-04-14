from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from django_countries.fields import CountryField


class UserProfile(models.Model):
    """
    A user profile model for storing delivery information and order history.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    default_street_address1 = models.CharField(max_length=80,
                                               null=True, blank=True)
    default_street_address2 = models.CharField(max_length=80,
                                               null=True, blank=True)
    default_town_or_city = models.CharField(max_length=40,
                                            null=True, blank=True)
    default_county = models.CharField(max_length=80, null=True, blank=True)
    default_postcode = models.CharField(max_length=20, null=True, blank=True)
    default_country = CountryField(blank_label="Select Your Country",
                                   null=True, blank=True)
    default_phone_number = models.CharField(max_length=20,
                                            null=True, blank=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Create of update the user profile
    """
    if created:
        UserProfile.objects.create(user=instance)
    else:
        UserProfile.objects.update_or_create(user=instance)
    # existing users save their profile
    instance.userprofile.save()


class MarketingEmail(models.Model):
    subject = models.CharField(max_length=255)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject


class EmailLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.ForeignKey(MarketingEmail, on_delete=models.CASCADE)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.email.subject}"
