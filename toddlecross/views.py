from django.shortcuts import render
from django.contrib.auth.decorators import login_required, login_not_required

@login_not_required
def home_view(request):
    if request.user.is_authenticated:
        return render(request, 'toddlecross/dashboard.html')
    return render(request, 'toddlecross/login.html')
