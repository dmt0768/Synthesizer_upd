from django.db import models

class Lines(models.Model):
    id = models.IntegerField(primary_key=True)
    input_freq = models.IntegerField(blank=True, null=True)
    output_freq = models.IntegerField(blank=True, null=True)
    status = models.CharField(blank=True, max_length=500)
    turn_on = models.BooleanField(default=False)
    default_input_freq = models.IntegerField(blank=True, null=True)
    default_output_freq = models.IntegerField(blank=True, null=True)
    default_status = models.CharField(blank=True, max_length=500)
    default_turn_on = models.BooleanField(default=False)

    def __str__(self):
        return 'Линия № ' + str(self.id)

class Registers(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(blank=True, null=True, max_length=50)
    value = models.CharField(blank=True, null=True, max_length=20)
    default_value = models.CharField(blank=True, null=True, max_length=20)

