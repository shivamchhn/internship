from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.generic import View
from .forms import UserForm
from django.http import HttpResponseRedirect,HttpResponse
from django.urls import reverse


class UserFormView(View):
    form_class = UserForm
    template_name = 'signing/registration_form.html'

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form} )

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():

            user = form.save(commit=False)
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user.set_password(password)
            user.save()

            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                return render(request, template_name="signing/aftersignup.html", context={'user': user})

        return render(request, self.template_name, {'form': form})


def user_login(request):

    if request.method == "POST" :
        context = {}
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return HttpResponseRedirect(reverse(success))
        else:
            context["error"] = "provide valid credentials"
            return render(request, "signing/login_form.html", context)

    else:
        return render(request, "signing/login_form.html")


def success(request):
    context = {'user': request.user}
    return render(request, "signing/success.html", context)


def userlogout(request):
    if request.method == "POST":
        logout(request)
        return HttpResponseRedirect(reverse(user_login))








