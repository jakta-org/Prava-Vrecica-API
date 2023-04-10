from django.db import models


# create feedback model
class Feedback(models.Model):
    id = models.AutoField(primary_key=True)
    image = models.ImageField(upload_to='images/')
    frames_data = models.CharField(max_length=1000, blank=False, null=False)
    user_id = models.CharField(max_length=100)
    message = models.CharField(max_length=1000, default="")
    upload_date = models.DateTimeField(auto_now_add=True)
    is_correct = models.BooleanField(blank=True, null=True)
    detected_object_id = models.IntegerField(blank=False, null=False, default=0)
    correct_object_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.id)

# create Object model
class Object(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=5)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, default="")

    def __str__(self):
        return str(self.id)
    