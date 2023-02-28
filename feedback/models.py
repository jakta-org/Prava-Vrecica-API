from django.db import models


# create feedback model
class Feedback(models.Model):
    id = models.AutoField(primary_key=True)
    image = models.CharField(max_length=100)
    user_id = models.CharField(max_length=100)
    message = models.CharField(max_length=1000, default="")
    date = models.DateTimeField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)
    