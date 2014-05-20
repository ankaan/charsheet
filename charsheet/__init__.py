from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.config import Configurator
from pyramid.path import AssetResolver
from pyramid.security import ALL_PERMISSIONS

from deform import Form
from pkg_resources import resource_filename
from sqlalchemy import engine_from_config

from .models import Base
from .models import db
from .models import get_groups
from .models import get_root

resolver = AssetResolver()

def resolve(path):
    return resolver.resolve(path).abspath()

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    db.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings,root_factory=get_root)

    deform_templates = resource_filename('deform', 'templates')
    deform_search_path = (resolve('charsheet:templates/deform'), deform_templates)
    Form.set_zpt_renderer(deform_search_path)

    config.include('pyramid_persona')
    config.set_authentication_policy(AuthTktAuthenticationPolicy(
        settings.get('persona.secret', None),
        hashalg='sha512',
        callback=get_groups,
        ))

    config.include('pyramid_mako')

    config.add_static_view('static/charsheet', 'charsheet:static', cache_max_age=3600)
    config.add_static_view('static/deform', 'deform:static', cache_max_age=3600)
    config.scan()
    return config.make_wsgi_app()
