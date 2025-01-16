from django.db import models
import uuid


class Setting(models.Model):
    setting_key = models.CharField(max_length=50, primary_key=True)
    label = models.CharField(max_length=50)
    int_val = models.IntegerField(null=True)
    txt_val = models.CharField(max_length=250, null=True)
    is_txt = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.setting_key}-{self.int_val}{self.txt_val}"

    class Meta:
        db_table = 'setting'


class Bot(models.Model):
    uuid = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    title = models.CharField(max_length=40, null=True) 
    ingress = models.TextField(null=True)  
    prompt = models.TextField(null=True)
    model_id = models.ForeignKey('BotModel', on_delete=models.RESTRICT, db_column='model_id', related_name="bots_id", null=True)
    temperature = models.DecimalField(max_digits=2, decimal_places=1, default=1.0)
    avatar_scheme = models.CharField(max_length=50, null=True)
    prompt_visibility = models.BooleanField(default=True)
    library = models.BooleanField(default=False)
    is_audio_enabled = models.BooleanField(default=False)
    owner = models.CharField(max_length=50, null=True)
    allow_distribution = models.BooleanField(default=False)
    mandatory = models.BooleanField(default=False)
    img_bot = models.BooleanField(default=False)
    bot_info = models.TextField(null=True)

    def __str__(self):
        return f"{self.uuid}-{self.title}"
    
    class Meta:
        db_table = 'bot'


class BotModel(models.Model):
    model_id = models.AutoField(primary_key=True)
    deployment_id = models.CharField(max_length=36, null=True)
    provider = models.CharField(max_length=50)
    model_url = models.CharField(max_length=500, null=True)
    display_name = models.CharField(max_length=500, null=True)
    model_description = models.TextField(null=True)
    training_cutoff = models.CharField(max_length=200, null=True)
    retirement = models.CharField(max_length=200, null=True)
    filter = models.CharField(max_length=50, null=True)
    version = models.CharField(max_length=50, null=True)

    def __str__(self):
        return f"{self.deployment_id}-{self.display_name}"

    class Meta:
        db_table = 'bot_model'


class Favorite(models.Model):
    id = models.AutoField(primary_key=True)
    bot_id = models.ForeignKey(Bot, on_delete=models.CASCADE, db_column='bot_id', to_field='uuid', related_name="favorites")
    user_id = models.CharField(max_length=50)
    # created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'favorite'
        unique_together = ('bot_id', 'user_id')


class PromptChoice(models.Model):
    id = models.CharField(max_length=7, primary_key=True)
    bot_id = models.ForeignKey(Bot, on_delete=models.CASCADE, db_column='bot_id', to_field='uuid', related_name="prompt_choices")
    label = models.CharField(max_length=50)
    order = models.IntegerField()
    text = models.TextField(null=True) 

    class Meta:
        db_table = 'prompt_choice'

class ChoiceOption(models.Model):
    id = models.CharField(max_length=7, primary_key=True)
    choice_id = models.ForeignKey(PromptChoice, on_delete=models.CASCADE, db_column='choice_id', to_field='id', related_name="options")
    label = models.CharField(max_length=50)
    text = models.TextField(default="")
    order = models.IntegerField()
    is_default = models.BooleanField(default=False)

    class Meta:
        db_table = 'choice_option'

class School(models.Model):
    class AccessEnum(models.TextChoices):
        NONE = 'none'
        EMP = 'emp'
        ALL = 'all'
        LEVELS = 'levels'

    org_nr = models.CharField(max_length=20, primary_key=True)
    school_name = models.CharField(max_length=50, null=True, default='')  
    school_code = models.CharField(max_length=3, null=True)  
    access = models.CharField(max_length=10, choices=AccessEnum.choices, default=AccessEnum.NONE)

    def __repr__(self):
        return f"{self.org_nr}-{self.school_name}"

    class Meta:
        db_table = 'school'
        ordering = ['school_name']


class BotAccess(models.Model):
    class AccessEnum(models.TextChoices):
        NONE = 'none'
        EMP = 'emp'
        ALL = 'all'
        LEVELS = 'levels'

    access_id = models.AutoField(primary_key=True)
    bot_id = models.ForeignKey(Bot, on_delete=models.CASCADE, db_column='bot_id', to_field='uuid', related_name="accesses")
    school_id = models.ForeignKey(
        School, on_delete=models.CASCADE, db_column='school_id', to_field='org_nr', related_name="accesses")
    level = models.CharField(max_length=20, null=True) 
    access = models.CharField(max_length=10, choices=AccessEnum.choices, default=AccessEnum.NONE, null=True) 

    def __str__(self):
        return f"{self.bot_id}-{self.school_id}{self.level}"

    class Meta:
        db_table = 'bot_access'
        unique_together = ('bot_id', 'school_id')


class BotLevel(models.Model):
    level_id = models.AutoField(primary_key=True)
    access_id = models.ForeignKey(
        BotAccess, on_delete=models.CASCADE, db_column='access_id', related_name="levels")
    level = models.CharField(max_length=20, default='') 

    def __str__(self):
        return f"{self.level_id}-{self.access_id}{self.level}"
    
    class Meta:
        db_table = 'bot_level'


class SchoolAccess(models.Model):
    access_id = models.AutoField(primary_key=True)
    school_id = models.ForeignKey(
        School, on_delete=models.CASCADE, db_column='school_id', to_field='org_nr', related_name="school_accesses")
    level = models.CharField(max_length=20)

    def __str__(self):
        return f"global-{self.access_id}:{self.school_id}{self.level}"

    class Meta:
        db_table = 'school_access'


class SubjectAccess(models.Model):
    id = models.AutoField(primary_key=True)
    bot_id = models.ForeignKey(Bot, on_delete=models.CASCADE, 
                               db_column='bot_id', to_field='uuid', related_name="subjects")
    subject_id = models.CharField(max_length=200, null=True) 
    created = models.DateTimeField(auto_now_add=True) 

    class Meta:
        db_table = 'subject_access'
        unique_together = ('bot_id', 'subject_id')


class PageText(models.Model):
    page_id = models.CharField(max_length=10, primary_key=True)
    page_title = models.CharField(max_length=50)
    page_text = models.TextField(null=True) 
    public = models.BooleanField() 

    class Meta:
        db_table = 'page_text'


class Role(models.Model):
    class RoleEnum(models.TextChoices):
        ADMIN = 'admin'
        AUTHOR = 'author'
        EMP = 'emp'

    user_id = models.CharField(max_length=50, primary_key=True)
    role = models.CharField(max_length=10, choices=RoleEnum.choices, default=RoleEnum.EMP)
    school = models.ForeignKey(School, on_delete=models.CASCADE, db_column='school', to_field='org_nr', related_name="roles", null=True) 

    def __str__(self):
        return f"{self.user_id}-{self.role}"

    class Meta:
        db_table = 'role'


class UseLog(models.Model):
    id = models.AutoField(primary_key=True)
    role = models.CharField(max_length=20)
    level = models.IntegerField(null=True)
    bot_id = models.CharField(max_length=36)
    message_length = models.IntegerField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'use_log'
        ordering = ['-timestamp']


class LogSchool(models.Model):
    id = models.AutoField(primary_key=True)
    log_id = models.ForeignKey(UseLog, on_delete=models.CASCADE, db_column='log_id', related_name="schools")
    school_id = models.ForeignKey(School, on_delete=models.DO_NOTHING, db_column='school', related_name="school_logs")

    class Meta:
        db_table = 'log_school'
        unique_together = ('log_id', 'school_id')


class TagCategory(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=50)
    category_order = models.IntegerField(unique=True)

    def __str__(self):
        return f"{self.category_id}-{self.category_name}"

    class Meta:
        db_table = 'tag_category'


class TagLabel(models.Model):
    tag_label_id = models.AutoField(primary_key=True)
    tag_label_name = models.CharField(max_length=50)
    tag_label_order = models.IntegerField()
    category_id = models.ForeignKey(TagCategory, on_delete=models.CASCADE, db_column='category_id', to_field='category_id', related_name="tag_labels")

    def __str__(self):
        return f"{self.tag_label_id}-{self.tag_label_name}"
    
    class Meta:
        db_table = 'tag_label'
        unique_together = ('tag_label_order', 'category_id')


class Tag(models.Model):
    tag_id = models.AutoField(primary_key=True)
    tag_value = models.IntegerField()
    category_id = models.ForeignKey(TagCategory, on_delete=models.CASCADE, db_column='category_id', to_field='category_id', related_name="tags")
    bot_id = models.ForeignKey(Bot, on_delete=models.CASCADE, db_column='bot_id', to_field='uuid', related_name="tags")


    def __str__(self):
        return f"{self.tag_id}-{self.category_id}{self.bot_id}"
    
    class Meta:
        db_table = 'tag'
        unique_together = ('category_id', 'bot_id')
