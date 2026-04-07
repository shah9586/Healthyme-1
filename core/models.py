from django.db import models
from django.contrib.auth.models import AbstractUser


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