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