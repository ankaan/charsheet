import colander as co
import deform
import string

def resources(form):
    resources = form.get_widget_resources()
    js_resources = resources['js']
    css_resources = resources['css']
    js_links = ['deform:static/%s' % r for r in js_resources]
    css_links = ['deform:static/%s' % r for r in css_resources]
    return (css_links, js_links)



def error(form, fieldname=None, msg=None, topmsg=None):
    form.error = co.Invalid(form.schema, topmsg)
    if fieldname is not None:
        form[fieldname].error = co.Invalid(form.schema[fieldname], msg)


@co.deferred
def deferred_csrf_default(node, kw):
    request = kw.get('request')
    csrf_token = request.session.get_csrf_token()
    return csrf_token

@co.deferred
def deferred_csrf_validator(node, kw):
    def validate_csrf(node, value):
        request = kw.get('request')
        csrf_token = request.session.get_csrf_token()
        if value != csrf_token:
            raise ValueError('Bad CSRF token')
    return validate_csrf

class CSRFSchema(co.Schema):
    csrf = co.SchemaNode(
        co.String(),
        default = deferred_csrf_default,
        validator = deferred_csrf_validator,
        widget = deform.widget.HiddenWidget(),
        )

class Dictifier(list):
    def dictify(self, obj):
        d = {}
        for name in self:
            val = getattr(obj,name)
            if val is not None:
                d[name] = val
        return d

    def objectify(self, d, obj):
        for name in self:
            try:
                setattr(obj, name, d[name])
            except KeyError:
                pass

def chars(name):
    valid = string.digits + string.ascii_uppercase + string.ascii_lowercase + ' '
    return all( c in valid for c in name )

def doublespace(name):
    try:
        # Do not accept multiple consecutive whitespaces.
        name.index('  ')
        return False
    except ValueError:
        return True

sane_name = co.All(
        co.Length(min=2, max=20),
        co.Function(chars, msg="Name may only contain A-Z, a-z, 0-9, and space."),
        co.Function(doublespace, msg="Do not use excessive whitespaces."),
        )

lower_case = co.Function(lambda s: str(s).islower(), msg="Only lower case allowed.")
