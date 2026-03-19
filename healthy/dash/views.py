from urllib import request
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
# Create your views here.


@login_required(login_url="login")
def userDashboardView(request):
    return render(request,"dash/user_dashboard.html")



@login_required
def owner_dashboard(request_url="login"):#check in core.urls.py login name should exist..
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    total_reports = 0  # Replace later with real model

    context = {
        'total_users': total_users,
        'active_users': active_users,
        'total_reports': total_reports,
    }

    return render(request,'dash/owner_dashboard.html', context)
