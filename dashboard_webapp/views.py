from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import LoginForm, SignUpForm
from . import models

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.urls import reverse

import mysql.connector
import datetime
from django.core import serializers
from django.contrib.auth.models import User

# Create your views below

"""
def chart_view(request, selected_sensor):
    return render('includes/chart.html', {"selected_sensor": selected_sensor})
"""

def db_r_query(query, param):
    Connection = mysql.connector.connect(host="localhost", user="root", password="!password")
    Cursor = Connection.cursor(buffered=True)
    Connection.connect() 
    Cursor.execute("USE dashboard_webapp")
    try:
        Cursor.execute(query, param)
        returned_rows = Cursor.fetchall()
        Connection.close()
        return returned_rows
    except (mysql.connector.DatabaseError, mysql.connector.OperationalError) as e:
        Connection.close()
        return []


def fetch_unit_info(request, hdb_block, unit_number):
    unit_info = []

    ReturnedRows = db_r_query(
        "SELECT DISTINCT * FROM dashboard_webapp_raspberry_location WHERE hdb_block=%s AND unit_number=%s ORDER BY raspberry_id ASC", 
        [hdb_block, '#' + unit_number]
    )

    for info in ReturnedRows: 
        unit_info.append(info) 
    
    return JsonResponse(data={
        'unit_info': unit_info,             
    })
    

def fetch_units(request, hdb_block):
    units = []

    ReturnedRows = db_r_query("SELECT * FROM dashboard_webapp_raspberry_location WHERE hdb_block=%s", [hdb_block])  
    for household_unit in ReturnedRows: 
        units.append(household_unit) 
    
    return JsonResponse(data={
        'units': units,             
    })


def fetch_blocks(request):
    blocks = []

    ReturnedRows = db_r_query("SELECT DISTINCT(hdb_block) FROM dashboard_webapp_raspberry_location", [])  
    for household_block in ReturnedRows: 
        blocks.append(household_block) 
    
    return JsonResponse(data={
        'blocks': blocks,             
    })


def format_time_axis(capturedDate_str, startDate, endDate):
    # If same day, exclude date, show time in AM/PM on x-axis
    if startDate == endDate:    
        dt = datetime.datetime.strptime(capturedDate_str[11:16], '%H:%M').strftime('%I:%M %p')
        return dt

    # If same year, exclude year, show '13 Dec, 01:40 PM' on x-axis
    elif startDate[0:4] == endDate[0:4]:
        dt = datetime.datetime.strptime(capturedDate_str[0:16], '%Y-%m-%d %H:%M').strftime('%d %b, %I:%M %p')
        return dt

    # If different year, exclude time, show date on x-axis
    else:
        dt = datetime.datetime.strptime(capturedDate_str[0:16], '%Y-%m-%d %H:%M').strftime('%d %b %Y')
        return dt


def format_reading_to_threshold(room_raw_readings, returned_rows_threshold, room_rpi_id):
    room_occurence_list = []  # Where each element is { x:y } equivalent to { datetime:duration }

    threshold_co = 0
    threshold_nh3 = 0
    threshold_ch2o = 0
    threshold_hcn = 0
    threshold_voc = 0

    for rpi_threshold in returned_rows_threshold:
        if rpi_threshold[0] == room_rpi_id:
            threshold_co = rpi_threshold[1]
            threshold_nh3 = rpi_threshold[2]
            threshold_ch2o = rpi_threshold[3]
            threshold_hcn = rpi_threshold[4]
            threshold_voc = rpi_threshold[5]

    for reading in room_raw_readings:
        actual_co = reading[2]
        actual_nh3 = reading[3]
        actual_ch2o = reading[4]
        actual_hcn = reading[5]
        actual_voc = reading[6]

        if actual_co >= threshold_co and actual_nh3 >= threshold_nh3 and actual_ch2o >= threshold_ch2o and actual_hcn >= threshold_hcn and actual_voc >= threshold_voc:
            print('smoke occured!')
        else:
            print('no occurence')
    
    return []


def fetch_smoke_occurence(request, hdb_block, unit_no, startDate, startTime, endDate, endTime):
    data = [
        [], # for Bedroom 1 
        [], # for Bedroom 2 
        [], # for Bedroom 3 
        [], # for Living room 
        [], # for Kitchen 
    ]
    rpi_id_list = []

    # Get raspberry ids in chosen block and unit
    ReturnedRows1 = db_r_query(
        "SELECT raspberry_id, room_name FROM dashboard_webapp_raspberry_location WHERE hdb_block=%s AND unit_number=%s", 
        [hdb_block, '#' + unit_no]
    )   
    print('1st query executed')

    # If no raspberry exists at location, return nothing where data=[]
    if len(ReturnedRows1) == 0:
        return JsonResponse(data={      
            'data': data,                  
        })

    # Get list of rpi_id for next sql query
    for returnedRow1 in ReturnedRows1:
        rpi_id_list.append(str(returnedRow1[0]))

    # Add datetime range for next sql query
    query_datetime_start = startDate + " " + startTime + ":00"
    query_datetime_end = endDate + " " + endTime + ":00"
    query2_list = rpi_id_list
    query2_list.append(query_datetime_start)
    query2_list.append(query_datetime_end)

    # Remove last 2 items(datetimes) to get back raspberry ids as new list
    rpi_id_list = query2_list[:len(query2_list) - 2]

    # Get smoke readings for each raspberry id
    ReturnedRows2 = db_r_query(
        f"SELECT raspberry_id, captured_date, co, nh3, ch2o, hcn, voc FROM dashboard_webapp_smokereading WHERE raspberry_id IN ({','.join('%s' for rpi_id in rpi_id_list)}) AND (captured_date BETWEEN %s AND %s) ORDER BY captured_date", 
        query2_list
    )   
    print('2nd query executed')

    bedroom_1_raw_data = []
    bedroom_2_raw_data = []
    bedroom_3_raw_data = []
    living_room_raw_data = []
    kitchen_raw_data = []

    bedroom_1_rpi_id = 0
    bedroom_2_rpi_id = 0
    bedroom_3_rpi_id = 0
    living_room_rpi_id = 0
    kitchen_rpi_id = 0

    # Fill above lists with respective gas reading data + get rpi_id of each room
    for returnedRow2 in ReturnedRows2:              # Scan through gas reading data
        for returnedRow1 in ReturnedRows1:          # Scan through raspberry infos
            if returnedRow2[0] == returnedRow1[0]:  # If rpi_id matches, find out which room its located and add readings to respective raw data list
                if str(returnedRow1[1]) == 'Bedroom 1': 
                    bedroom_1_rpi_id = returnedRow1[0]
                    bedroom_1_raw_data.append(returnedRow2)
                elif str(returnedRow1[1]) == 'Bedroom 2':
                    bedroom_2_rpi_id = returnedRow1[0]
                    bedroom_2_raw_data.append(returnedRow2)
                elif str(returnedRow1[1]) == 'Bedroom 3':
                    bedroom_3_rpi_id = returnedRow1[0]
                    bedroom_3_raw_data.append(returnedRow2)
                elif str(returnedRow1[1]) == 'Living room':
                    living_room_rpi_id = returnedRow1[0]
                    living_room_raw_data.append(returnedRow2)
                elif str(returnedRow1[1]) == 'Kitchen':
                    kitchen_rpi_id = returnedRow1[0]
                    kitchen_raw_data.append(returnedRow2)

    # Get threshold level for each raspberry pi
    ReturnedRows3 = db_r_query(
        f"SELECT raspberry_id, co, nh3, ch2o, hcn, voc FROM dashboard_webapp_sensor_threshold WHERE raspberry_id IN ({','.join('%s' for rpi_id in rpi_id_list)})", 
        rpi_id_list
    ) 
    print('3rd query executed')

    # Function to determine whether each reading is a smoke occurence wrt rpi's threshold
    # + Get plot points as result {x: smoking duration (<5 mins interval check)), y: captured_datetime_start}
    if len(bedroom_1_raw_data) > 0:
        data[0] = format_reading_to_threshold(bedroom_1_raw_data, ReturnedRows3, bedroom_1_rpi_id)
        data[0] = [{'x': 10,'y': 10}, {'x': 16,'y': 28}, {'x': 16,'y': 5}]

    if len(bedroom_2_raw_data) > 0:
        data[1] = format_reading_to_threshold(bedroom_2_raw_data, ReturnedRows3, bedroom_2_rpi_id)
        data[1] = [{'x': 21,'y': 51}, {'x': 63,'y': 12}, {'x': 71,'y': 30}]

    if len(bedroom_3_raw_data) > 0:
        data[2] = format_reading_to_threshold(bedroom_3_raw_data, ReturnedRows3, bedroom_3_rpi_id)
        data[2] = [{'x': 94,'y': 53}, {'x': 36,'y': 24}, {'x': 84,'y': 49}]

    if len(living_room_raw_data) > 0:
        data[3] = format_reading_to_threshold(living_room_raw_data, ReturnedRows3, living_room_rpi_id)
        data[3] = [{'x': 92,'y': 13}, {'x': 64,'y': 25}, {'x': 16,'y': 10}]

    if len(kitchen_raw_data) > 0:
        data[4] = format_reading_to_threshold(kitchen_raw_data, ReturnedRows3, kitchen_rpi_id)
        data[4] = [{'x': 49,'y': 54}, {'x': 65,'y': 5}, {'x': 63,'y': 9}]


    return JsonResponse(data={      
        'data': data,                  
    })


def fetch_gas_reading(request, sensorId, startDate, startTime, endDate, endTime):
    labels = []
    data = []

    query_datetime_start = startDate + " " + startTime + ":00"
    query_datetime_end = endDate + " " + endTime + ":00"

    ReturnedRows = db_r_query(
        "SELECT captured_date, smoke_value FROM dashboard_webapp_smokereading WHERE raspberry_id=%s AND (captured_date BETWEEN %s AND %s) ORDER BY captured_date", 
        [sensorId, query_datetime_start, query_datetime_end]
    )                

    for smokeReading in ReturnedRows:   
        # Append to labels[] for x(time) axis
        capturedDate_str = str(smokeReading[0])
        dt = format_time_axis(capturedDate_str, startDate, endDate)
        print(dt)
        labels.append(str(dt))

        # Append to data[] for y axis
        data.append(smokeReading[1])    
    
    # Return to AJAX call 'success'
    return JsonResponse(data={
        'labels': labels,              
        'data': data,                  
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
    logout(request)
    return HttpResponseRedirect('/login/')


def register_user(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        print(form)
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
    context = {
        'segment': 'profile/',
    }
    html_template = loader.get_template('home/profile.html')
    return HttpResponse(html_template.render(context, request))


def table_view(request):
    context = {
        'segment': 'tables/',
    }
    html_template = loader.get_template('home/tables.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def index(request):
    context = {
        'segment': 'index',
    }
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
