from pyramid.httpexceptions import HTTPFound
from pyramid_persona.views import verify_login
from pyramid.response import Response
from pyramid.security import forget
from pyramid.security import remember
from pyramid.traversal import resource_path
from pyramid.view import forbidden_view_config
from pyramid.view import notfound_view_config
from pyramid.view import view_config

from webhelpers.paginate import PageURL_WebOb, Page
import deform
import deform.widget
import colander as co

import logging
log = logging.getLogger(__name__)

from .models import db
from .models import Root
from .models import User
from .models import Party
from .models import userlist
from .models import UserList
from .models import userregister
from .models import UserRegister
from .models import partylist
from .models import PartyList

import charsheet.formutils as formutils

from sqlalchemy.exc import DBAPIError
from sqlalchemy.exc import IntegrityError
from sqlalchemy import asc
from sqlalchemy.orm.exc import NoResultFound

@view_config(route_name='login', check_csrf=True, renderer='json')
def login_view(request):
    # Verify the assertion and get the email of the user
    email = verify_login(request).lower()

    # Add the headers required to remember the user to the response
    request.response.headers.extend(remember(request, email))

    try:
        user = db.query(User).filter(User.email == email).one()
        request.session.flash('User signed in.', queue='info')
        # Return a json message containing the address or path to redirect to.
        return {'redirect': request.POST['came_from'],
                'success': True
                }
    except NoResultFound:
        request.session.flash('New user detected.', queue='info')
        # Return a json message containing the path to the registration page.
        return {'redirect': resource_path(userregister),
                'success': True
                }

@view_config(route_name='logout', check_csrf=True, renderer='json')
def logout_view(request):
    request.response.headers.extend(forget(request))
    request.session.flash('User signed out.', queue='info')
    return {'redirect': resource_path(request.root)}

@view_config(context=User, name='', renderer='templates/user.mako', permission='view')
@view_config(context=User, name='view', renderer='templates/user.mako', permission='view')
def view_user(request):
    return {'request': request}


@view_config(context=User, name='delete', renderer='templates/userdelete.mako', permission='delete')
def delete_user(request):
    schema = formutils.CSRFSchema().bind(request=request)

    is_self = request.context == request.user

    form = deform.Form(
            schema,
            buttons=[
                deform.Button(
                    name='yes',
                    css_class='btn-danger',
                    ),
                deform.Button(
                    name='no',
                    )],
            formid='deleteuser',
            )

    try:
        if 'no' in request.POST:
            return HTTPFound(location = resource_path(request.context))
        elif 'yes' in request.POST:
            controls = request.POST.items()
            form.validate(controls)

            db.delete(request.context)
            db.commit()

            request.session.flash('User deleted successfully!', queue='success')

            if is_self:
                return HTTPFound(location = resource_path(userregister))
            else:
                return HTTPFound(location = resource_path(userlist))

    except ValueError as e:
        if e.message == "Bad CSRF token":
            request.session.flash('Warning: Bad CSRF token, another site may be trying to control your session!', queue='error')
            formutils.error(form)
        else:
            raise e

    except deform.ValidationFailure:
        if form['csrf'].error is not None:
            request.session.flash('Warning: Bad CSRF token, another site may be trying to control your session!', queue='error')

    css_resources, js_resources = formutils.resources(form)

    return {'form': form,
            'css_resources': css_resources,
            'js_resources': js_resources,
            }


@view_config(context=UserRegister, name='', renderer='templates/useredit.mako', permission='add')
@view_config(context=User, name='edit', renderer='templates/useredit.mako', permission='edit')
class EditUser(object):

    class EditSchema(formutils.CSRFSchema):
        name = co.SchemaNode(
                co.String(),
                default='',
                validator=formutils.sane_name,
                )

    class AdminSchema(EditSchema):
        email = co.SchemaNode(
                co.String(),
                validator=co.All(
                    formutils.lower_case,
                    co.Email(),
                    ),
                widget=deform.widget.CheckedInputWidget(),
                )
        admin = co.SchemaNode(co.Boolean())
        active_admin = co.SchemaNode(co.Boolean())

    def __init__(self, request):
        self.request = request

    def __call__(self):
        is_edit = isinstance(self.request.context, User)

        buttons = [
                deform.Button(
                    name='save',
                    ),
                deform.Button(
                    name='reset',
                    type='reset',
                    )]

        if is_edit and self.request.has_permission('admin'):
            dictifier = formutils.Dictifier(['name', 'email', 'admin', 'active_admin'])
            s = EditUser.AdminSchema()
        else:
            dictifier = formutils.Dictifier(['name'])
            s = EditUser.EditSchema()

        if self.request.has_permission('delete'):
            buttons.append(deform.Button(
                name='delete',
                css_class='btn-danger',
                ))

        schema = s.bind(request=self.request)

        if is_edit:
            user = self.request.context
        else:
            user = User(email = self.request.authenticated_userid)

        form = deform.Form(
                schema,
                buttons=buttons,
                formid='edituser',
                appstruct=dictifier.dictify(user),
                )

        try:
            if 'delete' in self.request.POST:
                return HTTPFound(location = resource_path(user,'@@delete'))

            elif 'save' in self.request.POST:
                controls = self.request.POST.items()
                appstruct = form.validate(controls)
                dictifier.objectify(appstruct, user)
                db.add(user)

                if is_edit:
                    location = resource_path(user)
                else:
                    location = resource_path(self.request.root)

                db.commit()

                if is_edit:
                    self.request.session.flash('User updated successfully!', queue='success')
                else:
                    self.request.session.flash('User registered successfully!', queue='success')

                return HTTPFound(location = location)

        except IntegrityError, e:
            db.rollback()

            message = e.orig.message
            pattern = "column %s is not unique"

            email_key = User.__mapper__.attrs['email'].columns[0].key
            name_key = User.__mapper__.attrs['name'].columns[0].key

            if message == pattern%email_key:
                formutils.error(form, fieldname='email', msg='Email must be unique.')
            elif message == pattern%name_key:
                formutils.error(form, fieldname='name', msg='Name must be unique.')
            else:
                self.request.session.flash('Integrity failure, something is wrong with the user. This should not happen.', queue='error')
                formutils.error(form)

        except ValueError as e:
            if e.message == "Bad CSRF token":
                self.request.session.flash('Warning: Bad CSRF token, another site may be trying to control your session!', queue='error')
                formutils.error(form)
            else:
                raise e

        except deform.ValidationFailure:
            if form['csrf'].error is not None:
                self.request.session.flash('Warning: Bad CSRF token, another site may be trying to control your session!', queue='error')

        css_resources, js_resources = formutils.resources(form)

        return {'form': form,
                'is_edit': is_edit,
                'css_resources': css_resources,
                'js_resources': js_resources,
                }


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
            items_per_page=20,
            )

    return {'request': request,
            'paginator': paginator,
            }

@view_config(context=PartyList, name='', renderer='templates/partylist.mako', permission='view')
@view_config(context=PartyList, name='view', renderer='templates/partylist.mako', permission='view')
def view_partylist(request):
    try:
        page = int(request.params.get('page', 1))
    except ValueError:
        page = 1

    if request.has_permission('admin'):
        query = Party.every()
    else:
        query = Party.by_user(request.user)

    page_url = PageURL_WebOb(request)
    paginator = Page(
            query,
            page,
            url=page_url,
            items_per_page=20,
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
    if request.user is None and request.context != userregister and request.has_permission('add',userregister):
        return HTTPFound(location = resource_path(userregister))
    else:
        return {'request': request}

@notfound_view_config(renderer='templates/notfound.mako')
def notfound(request):
    return {'request': request}
