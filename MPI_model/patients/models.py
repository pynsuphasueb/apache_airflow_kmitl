from django.db import models
import pytz
from datetime import datetime, timezone

# Create your models here.
class patients(models.Model):
    pid = models.AutoField(primary_key=True)
    HN = models.CharField(max_length=9)
    fname = models.CharField(max_length=30)
    lname = models.CharField(max_length=30)
    gender = models.IntegerField(default=0)

class patient_info(models.Model):
    no = models.AutoField(primary_key=True)
    date = models.DateTimeField(auto_now_add=False, auto_now=format(datetime.now(timezone.utc).astimezone(pytz.timezone('Asia/Bangkok')).astimezone()))
    age = models.IntegerField(default=0)
    BMI = models.DecimalField(max_digits=20, decimal_places=2)
    DM = models.IntegerField(default=0)
    HT = models.IntegerField(default=0)
    DLP = models.IntegerField(default=0)
    CKD = models.IntegerField(default=0)
    # LAD
    LAD4dmspect = models.DecimalField(max_digits=20, decimal_places=2)
    LADwallthick = models.DecimalField(max_digits=20, decimal_places=2)
    LADwallmotion = models.DecimalField(max_digits=20, decimal_places=2)
    LADCAG = models.IntegerField(default=0)
    # LCX
    LCX4dmspect = models.DecimalField(max_digits=20, decimal_places=2)
    LCXwallthick = models.DecimalField(max_digits=20, decimal_places=2)
    LCXwallmotion = models.DecimalField(max_digits=20, decimal_places=2)
    LCXCAG = models.IntegerField(default=0)
    # RCA
    RCA4dmspect = models.DecimalField(max_digits=20, decimal_places=2)
    RCAwallthick = models.DecimalField(max_digits=20, decimal_places=2)
    RCAwallmotion = models.DecimalField(max_digits=20, decimal_places=2)
    RCACAG = models.IntegerField(default=0)
    LVEF = models.IntegerField(default=0)
    CAG = models.IntegerField(default=0)
    CAG_confirm = models.IntegerField(default=0)
    pid = models.ForeignKey(patients, on_delete=models.CASCADE)