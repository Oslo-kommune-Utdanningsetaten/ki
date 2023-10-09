from flask import render_template, Blueprint


info = Blueprint('info', __name__, url_prefix='/info')

@info.route('/om')
def om():
    return render_template('om.html', page='om')

