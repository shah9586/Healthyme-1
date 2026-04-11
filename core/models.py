from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model




class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    contact = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.username


class ProductScan(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='scans', null=True, blank=True)
    product_name = models.CharField(max_length=255, blank=True, default='Unknown Product')
    health_score = models.IntegerField(default=0)
    grade = models.CharField(max_length=5, blank=True)
    summary = models.TextField(blank=True)
    positives = models.JSONField(default=list)
    negatives = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)
    scanned_at = models.DateTimeField(auto_now_add=True)
    points_earned = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.product_name} — {self.health_score}/100"
    

from django.db import models

class ProductIndex(models.Model):
    barcode = models.CharField(max_length=128, unique=True, db_index=True)
    name = models.TextField(blank=True, null=True)
    ingredients = models.TextField(blank=True, null=True)
    categories = models.TextField(blank=True, null=True)
    brands = models.TextField(blank=True, null=True)
    countries = models.TextField(blank=True, null=True)
    source = models.CharField(max_length=50, default="openfoodfacts")

    def __str__(self):
        return self.name or "Unknown"
    



class RewardWallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    total_scans = models.IntegerField(default=0)
    healthy_scans = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.points} points"


class RewardHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    points_added = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.points_added}"
    

User = get_user_model()


@receiver(post_save, sender=User)
def create_reward_wallet(sender, instance, created, **kwargs):
    if created:
        RewardWallet.objects.create(user=instance)




class ScanHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    barcode = models.CharField(max_length=100, blank=True, null=True)
    score = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    harmful_ingredients = models.TextField(blank=True, null=True)
    good_ingredients = models.TextField(blank=True, null=True)
    scanned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product_name} - {self.score}"
    
class CommunityPost(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.content[:30]}"