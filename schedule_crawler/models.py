from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

def dateStartValidator(value):
    dateStartValidator.lastValue = value

def dateEndValidator(value):
    if dateStartValidator.lastValue > value:
        raise ValidationError(
                'End Date should be later than start date'
            )


class ScheduleInfo(models.Model):
    name = models.CharField(max_length=300)
    dateStart = models.DateTimeField(validators=[dateStartValidator,])
    dateEnd = models.DateTimeField(validators=[dateEndValidator,])
    
    def __str__(self):
        return timezone.localtime(self.dateStart).strftime("[%Y-%m-%d]") + "~" + timezone.localtime(self.dateStart).strftime("[%Y-%m-%d]") + " " + self.name
    
    def __eq__(self, other):
        return self.name==other.name and self.dateStart==other.dateStart and self.dateEnd==other.dateEnd


    
