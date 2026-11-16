from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from experiencias.models import Experience


def home_view(request):
    experiences = (
        Experience.objects.filter(
            is_active=True,
            category__is_active=True,
            scheduled_at__gte=timezone.now(),
        )
        .select_related('category')
        .order_by('scheduled_at')[:6]
    )
    return render(request, 'core/home.html', {'experiences': experiences})


@login_required
def dashboard_view(request):
    return render(request, 'core/dashboard.html')
