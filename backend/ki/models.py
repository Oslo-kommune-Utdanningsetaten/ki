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
    title = models.CharField(max_length=40)
    ingress = models.TextField()
    prompt = models.TextField()
    model = models.CharField(max_length=20)
    temperature = models.DecimalField(max_digits=2, decimal_places=1, default=1.0)
    image = models.CharField(max_length=20, null=True)
    prompt_visibility = models.BooleanField(default=True)
    owner = models.CharField(max_length=50, null=True)

    class Meta:
        managed = False
        db_table = 'bot'

class PromptChoice(models.Model):
    id = models.CharField(max_length=7, primary_key=True)
    bot_nr = models.ForeignKey(Bot, on_delete=models.CASCADE, db_column='bot_nr', to_field='bot_nr', related_name="prompt_choices")
    label = models.CharField(max_length=50)
    text = models.TextField()

    class Meta:
        managed = False
        db_table = 'prompt_choice'

class ChoiceOption(models.Model):
    id = models.CharField(max_length=7, primary_key=True)
    choice_id = models.ForeignKey(PromptChoice, on_delete=models.CASCADE, db_column='choice_id', to_field='id', related_name="options")
    label = models.CharField(max_length=50)
    text = models.TextField()
    is_default = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'choice_option'

class School(models.Model):
    class AccessEnum(models.TextChoices):
        NONE = 'none'
        EMP = 'emp'
        ALL = 'all'
        LEVELS = 'levels'

    org_nr = models.CharField(max_length=20, primary_key=True)
    school_name = models.CharField(max_length=50)
    school_code = models.CharField(max_length=3)
    access = models.CharField(max_length=10, choices=AccessEnum.choices, default=AccessEnum.NONE)

    def __repr__(self):
        return f"{self.org_nr}-{self.school_name}"

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


class SchoolAccess(models.Model):
    access_id = models.AutoField(primary_key=True)
    school_id = models.ForeignKey(
        School, on_delete=models.CASCADE, db_column='school_id', to_field='org_nr', related_name="school_accesses")
    # school_id = models.CharField(max_length=20)
    level = models.CharField(max_length=20)

    def __str__(self):
        return f"global-{self.access_id}:{self.school_id}{self.level}"

    class Meta:
        managed = False
        db_table = 'school_access'


class SubjectAccess(models.Model):
    id = models.AutoField(primary_key=True)
    bot_nr = models.ForeignKey(Bot, on_delete=models.CASCADE,
                               db_column='bot_nr', to_field='bot_nr', related_name="subjects")
    subject_id = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'subject_access'
        unique_together = ('bot_nr', 'subject_id')


class PageText(models.Model):
    page_id = models.CharField(max_length=10, primary_key=True)
    page_title = models.CharField(max_length=50)
    page_text = models.TextField()
    public = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'page_text'
