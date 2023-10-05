from flask import render_template, Blueprint


info = Blueprint('info', __name__, url_prefix='/info')

@info.route('/om')
def om():
    return render_template('om.html', page='om')

@info.route('/personvern')
def personvern():
    return render_template('personvern.html', page='personvern')

@info.route('/lerere')
def lerere():
    return render_template('lerere.html', page='lerere')

@info.route('/elever')
def elever():
    return render_template('elever.html', page='elever')

