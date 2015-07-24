from datetime import datetime
from StringIO import StringIO
from zipfile import ZipFile, ZIP_DEFLATED
from json import JSONEncoder, dumps
from flask import current_app, make_response, render_template, request
from registry.forms import CheckIdForm, check
from registry.models import Group, Passport, Visit


def index():
    return render_template('tools/index.html')


def check_id():
    check_id = None
    form = CheckIdForm(request.values, csrf_enabled=False)
    if form.validate():
        pass_id = form.pass_id.data
        check_id = check(pass_id)
    return render_template('tools/check-id.html', form=form, check_id=check_id)


def dump():
    data = {
        'Group': Group.query.all(),
        'Passport': Passport.query.all(),
        'Visit': Visit.query.all()
    }

    indent = None
    separators = (',', ':')

    if current_app.config['JSONIFY_PRETTYPRINT_REGULAR'] \
       and not request.is_xhr:
        indent = 2
        separators = (', ', ': ')

    class Encoder(JSONEncoder):

        def default(self, obj):
            if hasattr(obj, '__to_dict__'):
                return obj.__to_dict__()

            return JSONEncoder.default(self, obj)

    data = dumps(data, indent=indent, separators=separators,
                 cls=Encoder)

    zip_memory = StringIO()
    zipfile = ZipFile(zip_memory, compression=ZIP_DEFLATED, mode='w')
    when = datetime.now()
    zipfile.writestr('dump-{}.json'.format(when.isoformat()), data)
    zipfile.close()

    rv = make_response(zip_memory.getvalue())
    rv.headers['Content-Type'] = 'application/zip'
    filename = 'registry-{}.zip'.format(when.isoformat())
    cd = 'attachment; filename="{}"'.format(filename)
    rv.headers['Content-Disposition'] = cd
    return rv
