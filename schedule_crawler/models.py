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
    description = models.CharField(max_length=600, null=True, blank=True)
    dateStart = models.DateField(validators=[dateStartValidator,])
    dateEnd = models.DateField(validators=[dateEndValidator,])
    

    def __str__(self):
        return self.name

    
