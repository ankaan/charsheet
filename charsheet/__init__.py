from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from pyramid.security import ALL_PERMISSIONS
from pyramid.authentication import AuthTktAuthenticationPolicy

from .models import (
    db,
    Base,
    get_root,
    get_groups,
    )

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    db.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings,root_factory=get_root)

    config.include('pyramid_persona')
    config.set_authentication_policy(AuthTktAuthenticationPolicy(
        settings.get('persona.secret', None),
        hashalg='sha512',
        callback=get_groups,
        ))

    config.include('pyramid_mako')
    config.include('deform_bootstrap')

    config.add_static_view('static/charsheet', 'charsheet:static', cache_max_age=3600)
    config.add_static_view('static/deform', 'deform:static', cache_max_age=3600)
    config.scan()
    return config.make_wsgi_app()
