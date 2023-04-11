from django.db import models

class Feedback(models.Model):
    id = models.AutoField(primary_key=True)
    image = models.ImageField(upload_to='images/') # path
    objects_data = models.JSONField(blank=True, null=True)
    user_id = models.CharField(max_length=100)
    upload_date = models.DateTimeField(auto_now_add=True)
    is_trusted = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)
    
class RecognitionObject(models.Model):
    id = models.AutoField(primary_key=True)
    tag = models.CharField(max_length=100)
    meta_data = models.CharField(max_length=1000, blank=True, null=True)

    def __str__(self):
        return str(self.id)
    