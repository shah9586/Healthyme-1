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