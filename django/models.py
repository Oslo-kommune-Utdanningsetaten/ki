# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Bot(models.Model):
    bot_nr = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=20, blank=True, null=True)
    ingress = models.TextField(blank=True, null=True)
    prompt = models.TextField(blank=True, null=True)
    model = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bot'


class BotAccess(models.Model):
    access_id = models.AutoField(primary_key=True)
    bot_nr = models.IntegerField(blank=True, null=True)
    school_id = models.CharField(max_length=20, blank=True, null=True)
    level = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bot_access'


class School(models.Model):
    school_name = models.CharField(max_length=50, blank=True, null=True)
    school_code = models.CharField(max_length=3, blank=True, null=True)
    org_nr = models.CharField(primary_key=True, max_length=20)

    class Meta:
        managed = False
        db_table = 'school'


class Setting(models.Model):
    setting_key = models.CharField(primary_key=True, max_length=50)
    label = models.CharField(max_length=50)
    int_val = models.IntegerField(blank=True, null=True)
    txt_val = models.CharField(max_length=250, blank=True, null=True)
    is_txt = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'setting'
