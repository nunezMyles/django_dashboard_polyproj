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

import io
import PIL.Image as Image
import base64

# Create your views below

"""
def chart_view(request, selected_sensor):
    return render('includes/chart.html', {"selected_sensor": selected_sensor})
"""

def db_retrieve(query, param):
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


def fetch_unitInfo(request, hdb_block, unit_number):
    unit_info = []
    rpiLoc_id_list = [0, 0, 0, 0, 0] # where each item represents each room order of Bedroom1, Bedroom 2..., Kitchen

    ReturnedRows = db_retrieve(
        "SELECT * FROM dashboard_webapp_raspberry_location WHERE hdb_block=%s AND unit_number=%s ORDER BY raspberry_id ASC", 
        [hdb_block, '#' + unit_number]
    )

    for info in ReturnedRows: 
        unit_info.append(info) 

        if str(info[4]) == 'Bedroom 1':
            rpiLoc_id_list[0] = info[0]
        if str(info[4]) == 'Bedroom 2':
            rpiLoc_id_list[1] = info[0]
        if str(info[4]) == 'Bedroom 3':
            rpiLoc_id_list[2] = info[0]
        if str(info[4]) == 'Living room':
            rpiLoc_id_list[3] = info[0]
        if str(info[4]) == 'Kitchen':
            rpiLoc_id_list[4] = info[0]

    
    return JsonResponse(data={
        'unit_info': unit_info,   
        'rpiLocIds': rpiLoc_id_list   
    })
    

def fetch_units(request, hdb_block):
    units = []

    ReturnedRows = db_retrieve("SELECT * FROM dashboard_webapp_raspberry_location WHERE hdb_block=%s", [hdb_block])  
    for household_unit in ReturnedRows: 
        units.append(household_unit) 
    
    return JsonResponse(data={
        'units': units,             
    })


def fetch_blocks(request):
    blocks = []

    ReturnedRows = db_retrieve("SELECT DISTINCT(hdb_block) FROM dashboard_webapp_raspberry_location", [])  
    for household_block in ReturnedRows: 
        blocks.append(household_block) 
    
    return JsonResponse(data={
        'blocks': blocks,             
    })


def format_time_display(capturedDate_str_list, startDate, endDate):
    formatted_date_list = []

    # If same day, exclude date, show time in AM/PM on x-axis
    if startDate == endDate:    
        for date_str in capturedDate_str_list:
            dt = datetime.datetime.strptime(date_str[11:16], '%H:%M').strftime('%I:%M %p')
            dt_str = str(dt)
            formatted_date_list.append(dt_str)
        return formatted_date_list

    # If same year, exclude year, show '13 Dec, 01:40 PM' on x-axis
    elif startDate[0:4] == endDate[0:4]:
        for date_str in capturedDate_str_list:
            dt = datetime.datetime.strptime(date_str[0:16], '%Y-%m-%d %H:%M').strftime('%d %b, %I:%M %p')
            dt_str = str(dt)
            formatted_date_list.append(dt_str)
        return formatted_date_list

    # If different year, exclude time, show date on x-axis
    else:
        for date_str in capturedDate_str_list:
            dt = datetime.datetime.strptime(date_str[0:16], '%Y-%m-%d %H:%M').strftime('%d %b %Y')
            dt_str = str(dt)
            formatted_date_list.append(dt_str)
        return formatted_date_list


no_smoke_interval = datetime.timedelta(minutes=2)

def determine_smokeEvent(room_name, room_rawReadings, threshold_rooms_list, room_rpiId, startDate, endDate):
    smokeEvent_list = []
    smokeEvent_list_listview = []
    smokeEvent_list_scatterChart = [] # Where each element is { x:y } equivalent to { datetime:duration }

    # SCATTER CHART DATA STAGE

    # Scatter chart y-axis config
    scatter_y = 0 
    if room_name == 'Bedroom 1':
        scatter_y = 0
    elif room_name == 'Bedroom 2':
        scatter_y = 20
    elif room_name == 'Bedroom 3':
        scatter_y = 40
    elif room_name == 'Living room':
        scatter_y = 60
    elif room_name == 'Kitchen':
        scatter_y = 80

    threshold_co = 0
    threshold_nh3 = 0
    threshold_ch2o = 0
    threshold_hcn = 0
    threshold_voc = 0

    for rpi_threshold in threshold_rooms_list:
        if rpi_threshold[0] == room_rpiId:
            threshold_co = rpi_threshold[1]
            threshold_nh3 = rpi_threshold[2]
            threshold_ch2o = rpi_threshold[3]
            threshold_hcn = rpi_threshold[4]
            threshold_voc = rpi_threshold[5]

    for reading in room_rawReadings:
        actual_co = reading[2]
        actual_nh3 = reading[3]
        actual_ch2o = reading[4]
        actual_hcn = reading[5]
        actual_voc = reading[6]

        #if actual_co >= threshold_co and actual_nh3 >= threshold_nh3 and actual_ch2o >= threshold_ch2o and actual_hcn >= threshold_hcn and actual_voc >= threshold_voc:
        if actual_voc >= 11000:
            # Convert sql datetime to millisec for javascript to display on x-axis as time
            dt_sec = reading[1].timestamp()
            dt_millisec = dt_sec * 1000

            smokeEvent_list.append(reading[1])
    
    smokeSession_list = []

    # ALGORITHM TO GET EACH & EVERY SMOKING SESSION FROM LIST OF ALL SMOKING EVENTS
    if len(smokeEvent_list) > 1:
        smokeSession = []   # Where 1 smokeSession = Multiple smokeEvents
                            # & where the last smokeEvent of each smokeSession is at least 5mins long before the next smokeSession
                            
        # Preset 1st item of 1st cycle
        smokeSession.append(smokeEvent_list[0])
        smokeEvent_list.pop(0)           
                
        for dt in smokeEvent_list:
            dt_diff = dt - smokeSession[-1]
            # If no-smoke interval is lesser than 5 mins, add session to current cycle
            if dt_diff < no_smoke_interval:
                smokeSession.append(dt)
                # If very last smokeEvent of that room, save current cycle + end session checking
                if dt == smokeEvent_list[-1]:
                    smokeSession_list.append(smokeSession[:]) # Used [:] to troubleshoot append duplication bug
                    smokeEvent_list_scatterChart.append(smokeSession[:])
                    break
            # Else, reset cycle + preset brand new starting point for next cycle
            else:
                smokeSession_list.append(smokeSession[:])
                smokeEvent_list_scatterChart.append(smokeSession[:])
                smokeSession.clear()
                smokeSession.append(dt)

    elif len(smokeEvent_list) == 1:
        smokeSession_list.append([smokeEvent_list[0]])
        smokeEvent_list_scatterChart.append([smokeEvent_list[0]])

    # Scatter Chart showLine config
    for session in smokeEvent_list_scatterChart:
        for dt in session:
            dt_sec = dt.timestamp()
            dt_millisec = dt_sec * 1000

            # Convert event in session list into a scatter plot dataset
            session[session.index(dt)] = { "x": dt_millisec, "y": scatter_y }

    # DOUGHNUT CHARTS + LISTVIEW DATA STAGE
    room_smoking_duration_mins = 0
    smoking_freq = len(smokeSession_list)

    for session in smokeSession_list:

        # Format datetime for nice display
        unformatted_dt_start = str(session[0])
        unformatted_dt_end = str(session[-1])
        new_datetime_labels = format_time_display([unformatted_dt_start, unformatted_dt_end], startDate, endDate)
        formatted_dt_start = new_datetime_labels[0]
        formatted_dt_end = new_datetime_labels[1]

        session_duration = session[-1] - session[0]
        session_duration_mins = (session_duration.seconds + 60 // 2) // 60  # Round seconds to nearest minute
        room_smoking_duration_mins += session_duration_mins

        # Format duration display for listview item
        session_duration_label = ''
        if session_duration_mins == 1 and session_duration.seconds < 60:
            session_duration_label = str(session_duration.seconds) + ' sec'
        elif session_duration.seconds == 0:
            session_duration_label = 'Fail to determine duration'
        else:
            session_duration_label = str(session_duration_mins) + ' mins'

        smokeEvent_list_listview.append([room_name, formatted_dt_start, formatted_dt_end, session_duration_label])

    return smokeEvent_list_scatterChart, room_smoking_duration_mins, smokeEvent_list_listview, smoking_freq


def fetch_smokeEvent(request, hdb_block, unit_no, startDate, startTime, endDate, endTime):
    scatterChartData = [
        [], # for Bedroom 1 
        [], # for Bedroom 2 
        [], # for Bedroom 3 
        [], # for Living room 
        [], # for Kitchen 
    ]
    doughnutChartData_freq = [0, 0, 0, 0, 0]
    doughnutChartData_duration = [0, 0, 0, 0, 0]
    listViewData = [[], [], [], [], []]
    rpiId_list = []

    # Get raspberry ids in chosen block and unit
    ReturnedRows1 = db_retrieve(
        "SELECT `id`, raspberry_id, room_name FROM dashboard_webapp_raspberry_location WHERE hdb_block=%s AND unit_number=%s", 
        [hdb_block, '#' + unit_no]
    )  

    # If no raspberry exists at location, return nothing where data=[]
    if len(ReturnedRows1) == 0:
        return JsonResponse(data={      
            'data': scatterChartData,                  
        })

    for row in ReturnedRows1:
        rpiId_list.append(str(row[1]))

    # Add datetime range for next sql query
    query_datetime_start = startDate + " " + startTime + ":00"
    query_datetime_end = endDate + " " + endTime + ":00"
    query2_list = rpiId_list
    query2_list.append(query_datetime_start)
    query2_list.append(query_datetime_end)

    # Remove last 2 items(datetimes) to get back raspberry ids as new list
    rpiId_list = query2_list[:len(query2_list) - 2]

    # Get smoke readings for each raspberry id
    ReturnedRows2 = db_retrieve(
        f"SELECT raspberry_id, captured_date, co, nh3, ch2o, hcn, voc FROM dashboard_webapp_smokereading WHERE raspberry_id IN ({','.join('%s' for rpi_id in rpiId_list)}) AND (captured_date BETWEEN %s AND %s) ORDER BY captured_date", 
        query2_list
    )  

    bedroom_1_rawData = []
    bedroom_2_rawData = []
    bedroom_3_rawData = []
    livingRoom_rawData = []
    kitchen_rawData = []

    bedroom_1_rpiId = 0
    bedroom_2_rpiId = 0
    bedroom_3_rpiId = 0
    livingRoom_rpiId = 0
    kitchen_rpiId = 0

    # Fill above lists with respective gas reading data + get rpi_id of each room
    for row2 in ReturnedRows2:              # Scan through gas reading data
        for row1 in ReturnedRows1:          # Scan through raspberry infos
            if row2[0] == row1[1]:          # If rpi_id matches, find out which room its located and add readings to respective raw data list
                if str(row1[2]) == 'Bedroom 1': 
                    bedroom_1_rpiId = row1[1]
                    bedroom_1_rawData.append(row2)
                elif str(row1[2]) == 'Bedroom 2':
                    bedroom_2_rpiId = row1[1]
                    bedroom_2_rawData.append(row2)
                elif str(row1[2]) == 'Bedroom 3':
                    bedroom_3_rpiId = row1[1]
                    bedroom_3_rawData.append(row2)
                elif str(row1[2]) == 'Living room':
                    livingRoom_rpiId = row1[1]
                    livingRoom_rawData.append(row2)
                elif str(row1[2]) == 'Kitchen':
                    kitchen_rpiId = row1[1]
                    kitchen_rawData.append(row2)

    # Get threshold level for each raspberry pi
    ReturnedRows3 = db_retrieve(
        f"SELECT raspberry_id, co, nh3, ch2o, hcn, voc FROM dashboard_webapp_sensor_threshold WHERE raspberry_id IN ({','.join('%s' for rpi_id in rpiId_list)})", 
        rpiId_list
    )

    # Function to determine whether each reading is a smoke occurence wrt rpi's threshold
    # + Get plot points as result {x: smoking duration (<5 mins interval check)), y: captured_datetime_start}
    if len(bedroom_1_rawData) > 0:
        scatterChartData[0], doughnutChartData_duration[0], listViewData[0], doughnutChartData_freq[0] = determine_smokeEvent('Bedroom 1', bedroom_1_rawData, ReturnedRows3, bedroom_1_rpiId, startDate, endDate)

    if len(bedroom_2_rawData) > 0:
        scatterChartData[1], doughnutChartData_duration[1], listViewData[1], doughnutChartData_freq[1] = determine_smokeEvent('Bedroom 2', bedroom_2_rawData, ReturnedRows3, bedroom_2_rpiId, startDate, endDate)

    if len(bedroom_3_rawData) > 0:
        scatterChartData[2], doughnutChartData_duration[2], listViewData[2], doughnutChartData_freq[2] = determine_smokeEvent('Bedroom 3', bedroom_3_rawData, ReturnedRows3, bedroom_3_rpiId, startDate, endDate)

    if len(livingRoom_rawData) > 0:
        scatterChartData[3], doughnutChartData_duration[3], listViewData[3], doughnutChartData_freq[3] = determine_smokeEvent('Living room', livingRoom_rawData, ReturnedRows3, livingRoom_rpiId, startDate, endDate)

    if len(kitchen_rawData) > 0:
        scatterChartData[4], doughnutChartData_duration[4], listViewData[4], doughnutChartData_freq[4] = determine_smokeEvent('Kitchen', kitchen_rawData, ReturnedRows3, kitchen_rpiId, startDate, endDate)

    return JsonResponse(data={      
        'scatterChartData': scatterChartData,   
        'doughnutChartDataDuration': doughnutChartData_duration,
        'listViewData': listViewData,
        'doughnutChartDataFreq': doughnutChartData_freq,
    })


def fetch_gasReading(request, rpiId, startDate, startTime, endDate, endTime):
    labels = []

    co_actual_data = []
    nh3_actual_data = []
    ch2o_actual_data = []
    hcn_actual_data = []
    voc_actual_data = []

    co_threshold_data = []
    nh3_threshold_data = []
    ch2o_threshold_data = []
    hcn_threshold_data = []
    voc_threshold_data = []

    query_datetime_start = startDate + " " + startTime + ":00"
    query_datetime_end = endDate + " " + endTime + ":00"

    # Get gas readings
    ReturnedRows1 = db_retrieve(
        "SELECT captured_date, co, nh3, ch2o, hcn, voc FROM dashboard_webapp_smokereading WHERE raspberry_id=%s AND (captured_date BETWEEN %s AND %s) ORDER BY captured_date", 
        [rpiId, query_datetime_start, query_datetime_end]
    )

    # Get threshold level
    ReturnedRows2 = db_retrieve(
        "SELECT co, nh3, ch2o, hcn, voc FROM dashboard_webapp_sensor_threshold WHERE raspberry_id=%s", 
        [rpiId]
    )

    co_threshold = ReturnedRows2[0][0]
    nh3_threshold = ReturnedRows2[0][1]
    ch2o_threshold = ReturnedRows2[0][2]
    hcn_threshold = ReturnedRows2[0][3]
    voc_threshold = ReturnedRows2[0][4]

    # X-axis values
    capturedDate_str_list = []
    for smokeReading in ReturnedRows1:
        capturedDate_str = str(smokeReading[0])
        capturedDate_str_list.append(capturedDate_str)
    labels = format_time_display(capturedDate_str_list, startDate, endDate)

    # Y-axis values
    for smokeReading in ReturnedRows1:
        co_actual_data.append(smokeReading[1])
        nh3_actual_data.append(smokeReading[2])
        ch2o_actual_data.append(smokeReading[3])
        hcn_actual_data.append(smokeReading[4])
        voc_actual_data.append(smokeReading[5])

        co_threshold_data.append(co_threshold)
        nh3_threshold_data.append(nh3_threshold)
        ch2o_threshold_data.append(ch2o_threshold)
        hcn_threshold_data.append(hcn_threshold)
        voc_threshold_data.append(voc_threshold)


    # Return to AJAX call 'success'
    return JsonResponse(data={
        'labels': labels,         

        'co_actual_data': co_actual_data,      
        'nh3_actual_data': nh3_actual_data,   
        'ch2o_actual_data': ch2o_actual_data,   
        'hcn_actual_data': hcn_actual_data,   
        'voc_actual_data': voc_actual_data,   
        
        'co_threshold_data': co_threshold_data,   
        'nh3_threshold_data': nh3_threshold_data,   
        'ch2o_threshold_data': ch2o_threshold_data,   
        'hcn_threshold_data': hcn_threshold_data,   
        'voc_threshold_data': voc_threshold_data,               
    })


def fetch_image(request, rpiId, datetime_ms):

    # Pass datetime over to modal title in html
    dt = datetime.datetime.fromtimestamp(datetime_ms / 1000.0)

    # Include 3s mqtt trasnsfer delay
    dt_query_start = datetime.datetime.fromtimestamp((datetime_ms - 3000) / 1000.0)
    dt_query_end = datetime.datetime.fromtimestamp((datetime_ms + 3000) / 1000.0)

    print(dt_query_start, dt_query_end)

    # Retrieve BLOB imgs from db
    Thermal_ReturnedRows = db_retrieve(
        "SELECT `image` FROM dashboard_webapp_thermalcaptures WHERE raspberry_id=%s AND (captured_date BETWEEN %s AND %s)", 
        [rpiId, dt_query_start, dt_query_end]
    )

    Rgb_ReturnedRows = db_retrieve(
        "SELECT `image` FROM dashboard_webapp_rgbcaptures WHERE raspberry_id=%s AND (captured_date BETWEEN %s AND %s)", 
        [rpiId, dt_query_start, dt_query_end]
    )

    # If empty response, return nothing
    if len(Thermal_ReturnedRows) == 0 or len(Rgb_ReturnedRows) == 0:
        return JsonResponse(data={
        'thermalData': '',     
        'rgbData': '',   
        'datetime': str(dt),        
    })

    # Convert BLOB imgs -> str format -> set into html 'src' attribute
    buffered1 = io.BytesIO()
    thermal_img = Image.open(io.BytesIO(Thermal_ReturnedRows[0][0]))
    thermal_img.save(buffered1, format="JPEG")
    thermal_img_base64 = base64.b64encode(buffered1.getvalue())
    thermal_img_base64_str = "data:image/jpeg;base64, " + thermal_img_base64.decode("utf-8")

    buffered2 = io.BytesIO()
    rgb_img = Image.open(io.BytesIO(Rgb_ReturnedRows[0][0]))
    rgb_img.save(buffered2, format="JPEG")
    rgb_img_base64 = base64.b64encode(buffered2.getvalue())
    rgb_img_base64_str = "data:image/jpeg;base64, " + rgb_img_base64.decode("utf-8")

    return JsonResponse(data={
        'thermalData': thermal_img_base64_str,          
        'rgbData': rgb_img_base64_str, 
        'datetime': str(dt),     
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
