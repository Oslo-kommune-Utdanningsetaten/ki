from app import db
from flask import g


class Setting(db.Model):
    setting_key = db.Column(db.String(50), primary_key=True)
    label = db.Column(db.String(50), nullable=False)
    int_val =  db.Column(db.Integer)
    txt_val = db.Column(db.String(250))
    is_txt = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"{self.setting_key}-{self.int_val}{self.txt_val}"


class Bot(db.Model):
    bot_nr = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20))
    ingress = db.Column(db.Text)
    prompt = db.Column(db.Text)
    model = db.Column(db.String(20))
    image = db.Column(db.String(20))
    accesses = db.relationship('BotAccess', backref='bot')


class BotAccess(db.Model):
    access_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bot_nr = db.Column(db.Integer, db.ForeignKey('bot.bot_nr'))
    school_id = db.Column(db.String(50), db.ForeignKey('school.org_nr'))
    level = db.Column(db.String(20))

    def __repr__(self):
        return f"{self.bot_nr}-{self.school}{self.level}"


class School(db.Model):
    org_nr = db.Column(db.String(20), primary_key=True)
    # school_id = db.Column(db.Integer, primary_key=True)
    school_name = db.Column(db.String(50))
    school_code = db.Column(db.String(3))
    accesses = db.relationship('BotAccess', backref='school')


