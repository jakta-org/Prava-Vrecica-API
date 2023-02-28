from django.shortcuts import render

def get_update(request):
    return render(request, 'update/update.html')

def get_latest_ai_model(request):
    return render(request, 'update/update.html')

def get_latest_thresh_map(request):
    return render(request, 'update/update.html')