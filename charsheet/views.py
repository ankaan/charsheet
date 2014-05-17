from pyramid.response import Response
from pyramid.view import (
    view_config,
    forbidden_view_config,
    notfound_view_config,
    )

from sqlalchemy import asc
from sqlalchemy.exc import (
    DBAPIError,
    IntegrityError,
    )
from sqlalchemy.orm.exc import NoResultFound

from pyramid.traversal import resource_path
from pyramid.httpexceptions import HTTPFound

from .models import (
    db,
    User,
    UserList,
    Root,
    )

from pyramid_persona.views import verify_login
from pyramid.security import (
    remember,
    forget,
    )

from colanderalchemy import SQLAlchemySchemaNode
import deform
import colander

import transaction
from webhelpers.paginate import PageURL_WebOb, Page

@view_config(route_name='login', check_csrf=True, renderer='json')
def login(request):
    # Verify the assertion and get the email of the user
    email = verify_login(request).lower()

    # Add the headers required to remember the user to the response
    request.response.headers.extend(remember(request, email))

    try:
        user = db.query(User).filter(User.email == email).one()
    except NoResultFound:
        basename, _ = email.split('@', 1)
        basename = User.invalid_name_substr.sub(' ', basename).strip()

        success = False
        existing = map(lambda tup: tup[0],
                db.query(User.name)
                .filter( User.name.startswith(basename) ).all()
                )

        name = basename
        i = 0
        while name in existing:
            name = "%s%d" % (basename,i)
            i += 1

        user = User(name=name, email=email)
        db.merge(user)
        transaction.commit()
        # Return a json message containing the path to user configuration.
        return {'redirect': resource_path(user),
                'success': True
                }
    else:
        # Return a json message containing the address or path to redirect to.
        return {'redirect': request.POST['came_from'],
                'success': True
                }

@view_config(route_name='logout', check_csrf=True, renderer='json')
def logout(request):
    request.response.headers.extend(forget(request))
    return {'redirect': resource_path(request.root)}

@view_config(context=User, name='', renderer='templates/user.mako', permission='view')
@view_config(context=User, name='view', renderer='templates/user.mako', permission='view')
def view_user(request):
    return {'request': request}

@view_config(context=User, name='edit', renderer='templates/useredit.mako', permission='edit')
def edit_user(request):
    schema = SQLAlchemySchemaNode(
            User,
            includes=['name'],
            )

    form = deform.Form(
            schema,
            buttons=['save'],
            formid='edituser',
            appstruct=schema.dictify(request.context),
            )

    contextid = request.context.id
    userid = request.user.id
    try:
        if 'save' in request.POST:
            controls = request.POST.items()
            appstruct = form.validate(controls)
            updated = schema.objectify(appstruct, User(id = request.context.id))
            db.merge(updated)
            transaction.commit()
            return HTTPFound(location = resource_path(updated))
    except IntegrityError:
        transaction.abort()
        request.context = db.merge(User(id = contextid))
        request.user = db.merge(User(id = userid))
        form['name'].error = colander.Invalid(form.schema['name'], 'Duplicate name found.')
    except deform.ValidationFailure:
        pass
    return {'form': form}


@view_config(context=UserList, name='', renderer='templates/userlist.mako', permission='view')
@view_config(context=UserList, name='view', renderer='templates/userlist.mako', permission='view')
def view_userlist(request):
    try:
        page = int(request.params.get('page', 1))
    except ValueError:
        page = 1

    page_url = PageURL_WebOb(request)
    paginator = Page(
            User.every(),
            page,
            url=page_url,
            items_per_page=20
            )

    return {'request': request,
            'paginator': paginator,
            }

@view_config(context=Root, name='', renderer='templates/root.mako')
@view_config(context=Root, name='view', renderer='templates/root.mako')
def view_root(request):
    return {'request': request}

@forbidden_view_config(renderer='templates/forbidden.mako')
def forbidden(request):
    return {'request': request}

@notfound_view_config(renderer='templates/notfound.mako')
def notfound(request):
    return {'request': request}

def pager(paginator):
    return paginator.pager(
        format='$link_previous ~2~ $link_next',
        symbol_previous='< Previous',
        symbol_next='Next >',
        )
