import logging

from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect

log = logging.getLogger(__file__)


def login_view(request):
    """
    Return a login page after request

    Use @login_required
    from django.contrib.auth.decorators import login_required
    to mark views need login
    :param request:
    :return:
    """
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            log.info("User {} has login.".format(form.get_user()))
            return redirect("/")
        else:
            log.info("User {} login failed.".format(form.get_user()))
    else:
        # Not POST request, create a blank form
        form = AuthenticationForm()
    return render(request, 'login.html', context={'form': form})
