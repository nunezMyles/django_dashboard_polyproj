from django.shortcuts import HttpResponse, get_object_or_404, render
from . import models

# Create your views here.

#def index(request):
#    return HttpResponse("Hello, world. You're at the polls index.")
#def index(request):
#    return render(request, 'index.html')

def live_app(request):
    return render(request, 'live_app.html')

def shelter_list(request):
    shelters = models.Shelter.objects.all()
    context = {'shelters': shelters}
    return render(request, 'shelter_list.html', context)

def shelter_detail(request, pk):
    shelter = get_object_or_404(models.Shelter, pk=pk)
    context = {'shelter': shelter}
    return render(request, 'shelter_detail.html', context)