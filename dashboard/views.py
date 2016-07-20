from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import requests

@login_required
def purple_dashboard(request):
    request.breadcrumbs([("Dashboard", "")])
    user = ""
    secret = ""
    if "RED" in request.user.memberships:
        user = "r_user"
        secret = "enterRed"
    elif "AMBER" in request.user.memberships:
        user = "a_user"
        secret = "enterAmber"
    elif "GREEN" in request.user.memberships:
        user = "g_user"
        secret = "enterGreen"
    elif "WHITE" in request.user.memberships:
        user = "w_user"
        secret = "enterWhite"


    #response = requests.post(
    #    url='https://0.0.0.0:5601/api/shield/v1/login',
    #    verify=False,
    #    data={
    #                "username": "es_admin",
    #                "password": "HelloWorld"
    #            }
    #)
    #print response

    return render(request, "dashboard_new.html", {"user":user, "secret":secret})
