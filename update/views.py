import os
from django.forms import ValidationError
from rest_framework.views import APIView
from django.http import HttpRequest, JsonResponse
from django.http import HttpResponse
from .models import AI_regions
from . import settings
from rest_framework.permissions import IsAuthenticated

from rest_framework.parsers import MultiPartParser
class AImodelView(APIView):
    parser_classes = (MultiPartParser,)
    permission_classes = [IsAuthenticated]
    def get(self, request: HttpRequest, format=None):
        
        # get the last update date from the header
        params = request.META.get('params', None)
        if params is not None:
            last_update_date = params.get('If-Modified-Since', None)
        else:
            last_update_date = None

        # get the latest file from models
        latest_AI_region = AI_regions.objects.all().order_by('-upload_date').first()

        # if no model was found, return error
        if latest_AI_region is None:
            return HttpResponse(status=404, content='No model found')
        
        latest_model_date = str(latest_AI_region.upload_date)

        # if user didn't send last update date or the model is newer than the last update date 
        if last_update_date is None or latest_model_date > last_update_date:
            response = HttpResponse(content_type='application/octet-stream')
            response['Content-Disposition'] = 'attachment; filename="%s"' % latest_AI_region.file.name
            with latest_AI_region.file.open() as file:
                response.write(file.read())

            return response
        
        # if user has the latest model, return 304
        return HttpResponse(status=304)
        

    def post(self, request: HttpRequest, format=None):

        # get the file from the request
        file = request.FILES.get('ai_model')
        version = request.POST['version']

        # check if the file is valid
        if not AI_regions.is_valid_file(file):
            return HttpResponse(status=400, content='Invalid file')
        
        # get valid version
        try:
            version = AI_regions.get_valid_version(version)
        except ValidationError as e:
            return HttpResponse(status=400, content=e.message)
        
        # if version already exists, don't save the current file
        if AI_regions.objects.filter(version=version).exists():
            return HttpResponse(status=400, content='Version already exists')
        
        ai_region = AI_regions(version=version, file=file)
        
        # delete the oldest file if there are already n files stored
        if AI_regions.objects.count() >= settings.MAX_FILES_STORED:

            oldest_file = AI_regions.objects.first()
            # if the oldest file is newer than the current file, don't save the current file
            if oldest_file > ai_region:
                return HttpResponse(status=400, content='Version too old to upload')
            
            oldest_file.delete()


        ai_region.save()
        # return the success message
        return HttpResponse(status=201, content='File uploaded successfully')

    def put(self, request: HttpRequest, format=None):
        # print everything in the request
        print(request.POST)
        # get the file from the request
        # file = request.FILES.get('ai_model')
        file = request.body
        version = request.POST['version']
        
        # check if the file is valid
        if not AI_regions.is_valid_file(file):
            return HttpResponse(status=400, content='Invalid file')
    
        # get valid version
        try:
            version = AI_regions.get_valid_version(version)
        except ValidationError as e:
            return HttpResponse(status=400, content=e.message)
        
        # if version does not exist, return error
        if not AI_regions.objects.filter(version=version).exists():
            return HttpResponse(status=400, content='Version does not exist')
        
        # get the model with the given version
        ai_region = AI_regions.objects.get(version=version)

        # delete the old file
        ai_region.file.delete()
        
        # save the new file
        ai_region.file = file
        ai_region.save()

        # return the success message
        return HttpResponse(status=201, content='File uploaded successfully')
    
# same for mapping regions
class MappingRegionsView(APIView):
    def get(self, request, format=None):
        pass

class Updates(APIView):
    def get(request):
        pass