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
    UserRegister,
    userregister,
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

from webhelpers.paginate import PageURL_WebOb, Page

@view_config(route_name='login', check_csrf=True, renderer='json')
class LoginView(object):
    def __init__(self,request):
        self.request = request

    def __call__(self):
        # Verify the assertion and get the email of the user
        email = verify_login(self.request).lower()

        # Add the headers required to remember the user to the response
        self.request.response.headers.extend(remember(self.request, email))

        try:
            user = db.query(User).filter(User.email == email).one()
            # Return a json message containing the address or path to redirect to.
            return {'redirect': self.request.POST['came_from'],
                    'success': True
                    }
        except NoResultFound:
            # Return a json message containing the path to the registration page.
            return {'redirect': resource_path(userregister),
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

@view_config(context=UserRegister, name='', renderer='templates/register.mako', permission='add')
@view_config(context=User, name='edit', renderer='templates/useredit.mako', permission='edit')
def edit_user(request):
    is_edit = isinstance(request.context, User)

    schema = SQLAlchemySchemaNode(
            User,
            includes=['name'],
            )

    if is_edit:
        resource = request.context
    else:
        resource = User(email = request.authenticated_userid)

    form = deform.Form(
            schema,
            buttons=['save'],
            formid='edituser',
            appstruct=schema.dictify(resource),
            )

    try:
        if 'save' in request.POST:
            controls = request.POST.items()
            appstruct = form.validate(controls)
            schema.objectify(appstruct, resource)
            db.add(resource)

            if is_edit:
                location = resource_path(resource)
            else:
                location = resource_path(request.root)

            db.commit()

            return HTTPFound(location = location)
    except IntegrityError:
        db.rollback()
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

@view_config(context=Root, name='', renderer='templates/root.mako', permission='basic')
@view_config(context=Root, name='view', renderer='templates/root.mako', permission='basic')
def view_root(request):
    return {'request': request}

@forbidden_view_config(renderer='templates/forbidden.mako')
def forbidden(request):
    if request.user is None:
        return HTTPFound(location = resource_path(userregister))
    else:
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
