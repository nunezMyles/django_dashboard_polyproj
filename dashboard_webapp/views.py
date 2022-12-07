from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm, SignUpForm
from . import models

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.urls import reverse

import mysql.connector

# Create your views here

def line_graph(request):
    labels = []
    data = []

    Connection = mysql.connector.connect(host="localhost", user="root", password="!password")
    Cursor = Connection.cursor(buffered=True)

    Connection.connect() # start connection w/ MySQL

    # select the schema/database to use
    SQLQuery1 = "USE dashboard_webapp" 
    Cursor.execute(SQLQuery1)

    # select table to retrieve from
    SQLQuery2 = "SELECT * FROM dashboard_webapp_smokereading WHERE module_stand_id=1 ORDER BY captured_date" 
    Cursor.execute(SQLQuery2)

    ReturnedRows = Cursor.fetchall() # fetch query results from MySQL
    Connection.close() # close connection w/ MySQL

    # use for loop to go through each and every row result
    for smokeReading in ReturnedRows:  
        labels.append(smokeReading[2]) # for graph x-axis:  smokeReading[2] = captured_date
        data.append(smokeReading[1])   # for graph y-axis:  smoekReading[1] = smoke_value
    
    return JsonResponse(data={
        'labels': labels,   # return list of captured dates to line graph
        'data': data,       # return list of smoke values to lien graph
    })


def login_view(request):
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'

    return render(request, "authentication/login.html", {"form": form, "msg": msg})


def logout_view(request):
    return HttpResponseRedirect('/login/')


def register_user(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)

            msg = 'User created - please <a href="/login">login</a>.'
            success = True

            # return redirect("/login/")

        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()

    return render(request, "authentication/register.html", {"form": form, "msg": msg, "success": success})


def profile_view(request):
    context = {'segment': 'profile/'}
    html_template = loader.get_template('home/profile.html')
    return HttpResponse(html_template.render(context, request))


def table_view(request):
    context = {'segment': 'tables/'}
    html_template = loader.get_template('home/tables.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}
    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
            
        context['segment'] = load_template
        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))
