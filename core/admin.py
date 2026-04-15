from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect

class MyAdminSite(admin.AdminSite):
    site_header = "HealthyMe Admin"
    site_title = "HealthyMe Panel"
    index_title = "Welcome Admin"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('go-dashboard/', self.admin_view(self.go_dashboard))
        ]
        return custom_urls + urls

    def go_dashboard(self, request):
        return redirect('/admin-dashboard/')


admin_site = MyAdminSite(name='myadmin')

from django.contrib import admin
from .models import (
    CustomUser,
    ProductIndex,
    ScanHistory,
    RewardWallet,
    RewardHistory,
    CommunityPost,
    RegistrationOTP,
)

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'contact', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email', 'contact')
    list_filter = ('is_staff', 'is_superuser')


@admin.register(ProductIndex)
class ProductIndexAdmin(admin.ModelAdmin):
    list_display = ('id', 'barcode', 'name', 'brands', 'source')
    search_fields = ('barcode', 'name', 'brands')
    list_filter = ('source',)


@admin.register(ScanHistory)
class ScanHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product_name', 'score', 'status', 'scanned_at')
    search_fields = ('user__username', 'product_name', 'barcode')
    list_filter = ('status', 'scanned_at')


@admin.register(RewardWallet)
class RewardWalletAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'points', 'total_scans', 'healthy_scans')
    search_fields = ('user__username',)


@admin.register(RewardHistory)
class RewardHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'action', 'points_added', 'created_at')
    search_fields = ('user__username', 'action')
    list_filter = ('created_at',)


@admin.register(CommunityPost)
class CommunityPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'content', 'likes', 'created_at')
    search_fields = ('user__username', 'content')
    list_filter = ('created_at',)
    actions = ['delete_selected_posts']

    def delete_selected_posts(self, request, queryset):
        queryset.delete()
    delete_selected_posts.short_description = "Delete selected community posts"


@admin.register(RegistrationOTP)
class RegistrationOTPAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'contact', 'otp', 'is_verified', 'created_at')
    search_fields = ('email', 'contact')
    list_filter = ('is_verified', 'created_at')