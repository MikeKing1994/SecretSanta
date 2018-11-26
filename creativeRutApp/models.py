from django.db import models


class ParticipantName(models.Model):
    ParticipantName = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    def __str__(self):
        return self.ParticipantName


class ParticipantEmail(models.Model):
    pName = models.ForeignKey(ParticipantName, on_delete=models.CASCADE)
    pEmail= models.CharField(max_length=200)
    def __str__(self):
        return self.pEmail
    