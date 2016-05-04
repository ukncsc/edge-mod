from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def purple_dashboard(request):
    request.breadcrumbs([("Dashboard", "")])
    return render(request, "dashboard.html", {})
