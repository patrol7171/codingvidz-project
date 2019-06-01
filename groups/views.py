from django.shortcuts import render

def home (request):
    return render(request, 'groups/home.html')
