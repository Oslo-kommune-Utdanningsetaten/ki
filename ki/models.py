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
    image = models.CharField(max_length=20, null=True)
    owner = models.CharField(max_length=50, null=True)

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
        ordering = ['school_name']


class BotAccess(models.Model):
    access_id = models.AutoField(primary_key=True)
    bot_nr = models.ForeignKey(
        Bot, on_delete=models.CASCADE, db_column='bot_nr', related_name="accesses")
    # bot_nr = models.IntegerField()
    school_id = models.ForeignKey(
        School, on_delete=models.CASCADE, db_column='school_id', to_field='org_nr', related_name="accesses")
    # school_id = models.CharField(max_length=20)
    level = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.bot_nr}-{self.school_id}{self.level}"

    class Meta:
        managed = False
        db_table = 'bot_access'


class SubjectAccess(models.Model):
    id = models.AutoField(primary_key=True)
    bot_nr = models.ForeignKey(Bot, on_delete=models.CASCADE,
                               db_column='bot_nr', to_field='bot_nr', related_name="subjects")
    subject_id = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'subject_access'
        unique_together = ('bot_nr', 'subject_id')


class PageText(models.Model):
    page_id = models.CharField(max_length=10, primary_key=True)
    page_text = models.TextField()

    class Meta:
        managed = False
        db_table = 'page_text'
