from django.db import models

class Setting(models.Model):
    setting_key = models.CharField(max_length=50, primary_key=True)
    label = models.CharField(max_length=50)
    int_val = models.IntegerField(null=True)
    txt_val = models.CharField(max_length=250, null=True)
    is_txt = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.setting_key}-{self.int_val}{self.txt_val}"
    
    class Meta:
        managed = False
        db_table = 'setting'

class Bot(models.Model):
    bot_nr = models.AutoField(primary_key=True)
    title = models.CharField(max_length=20)
    ingress = models.TextField()
    prompt = models.TextField()
    model = models.CharField(max_length=20)
    image = models.CharField(max_length=20)
    owner = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'bot'

class School(models.Model):
    org_nr = models.CharField(max_length=20, primary_key=True)
    school_name = models.CharField(max_length=50)
    school_code = models.CharField(max_length=3)

    def __repr__(self):
        return f"{self.org_nr}"

    class Meta:
        managed = False
        db_table = 'school'
        

class BotAccess(models.Model):
    access_id = models.AutoField(primary_key=True)
    bot_nr = models.ForeignKey(Bot, on_delete=models.CASCADE, db_column='bot_nr')
    school_id = models.ForeignKey(School, on_delete=models.CASCADE, db_column='school_id', to_field='org_nr')
    level = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.bot_nr}-{self.school_id}{self.level}"
    
    class Meta:
        managed = False
        db_table = 'bot_access'

class SubjectAccess(models.Model):
    bot_nr = models.ForeignKey(Bot, on_delete=models.CASCADE)
    subject_id = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'subject_access'

