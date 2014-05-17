from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    String,
    Boolean,
    )

from sqlalchemy.orm.exc import NoResultFound

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from pyramid.security import (
    unauthenticated_userid,
    Allow,
    Everyone,
    Authenticated,
    DENY_ALL,
    )

from pyramid.events import NewRequest
from pyramid.events import subscriber

from string import digits, ascii_uppercase, ascii_lowercase
import re

db = scoped_session(sessionmaker())

@subscriber(NewRequest)
def begin_session(event):
    def end_session(request):
        db.remove()
    event.request.add_finished_callback(end_session)

Base = declarative_base()

Base.metadata.naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
    }

class Root(object):
    __name__ = None
    __parent__ = None
    __acl__ = [
            (Allow, 'group:active_admin', ('view','edit','add','admin')),
            ]

    __crumbs_name__ = 'Home'

    def __init__(self):
        self._children = {}

    def add(self,name,child):
        child.__name__ = name
        child.__parent__ = self
        self._children[name] = child

    def __getitem__(self,key):
        return self._children[key]

class UserList(object):
    __acl__ = [
            (Allow, 'group:admin', ('view','edit','add','admin')),
            (Allow, Authenticated, 'view'),
            ]

    __crumbs_name__ = 'User List'

    def __getitem__(self,key):
        try:
            return db.query(User).filter(User.name == key).one()
        except NoResultFound:
            raise KeyError(key)

root = Root()
userlist = UserList()
root.add('user',userlist)

class User(Base):
    __tablename__ = 'users'

    __parent__ = userlist

    @property
    def __name__(self):
        return self.name

    @property
    def __acl__(self):
        return [(Allow, self.email, ('view','edit'))]

    @property
    def __crumbs_name__(self):
        return self.name

    invalid_name_substr = re.compile(r'[^A-Za-z0-9]+')
    name_chars = ascii_uppercase + ascii_lowercase + digits
    
    @classmethod
    def checkname(cls,checkname):
        return all( c in cls.name_chars for c in checkname )

    @classmethod
    def every(cls): 
        return db.query(cls).order_by(User.name)

    id = Column(
            Integer,
            primary_key=True,
            info={'colanderalchemy': {
                'title': 'User ID',
                'exclude': True,
                }},
            )

    name = Column(
            String(length=20),
            nullable=False,
            index=True,
            unique=True,
            )

    email = Column(
            String(length=300),
            nullable=False,
            index=True,
            unique=True,
            )

    admin = Column(
            Boolean(name='admin'),
            nullable=False,
            default=False,
            info={'colanderalchemy': {
                'description': 'If user is admin.',
                }},
            )

    active_admin = Column(
            Boolean(name='active_admin'),
            nullable=False,
            default=False,
            info={'colanderalchemy': {
                'description': 'If user can bypass permissions.',
                }},
            )

    def groups(self):
        groups = []
        if self.admin:
            groups.append("group:admin")
        if self.active_admin:
            groups.append("group:active_admin")
        return groups

def get_root(request):
    return root

def get_user(request):
    user_id = unauthenticated_userid(request)
    if user_id is not None:
        return db.query(User).filter(User.email == user_id).first()

def get_groups(userid, request):
    if request.user is None:
        return None
    else:
        return request.user.groups()

def crumbs(context):
    def gen(resource):
        while resource is not None:
            if resource.__crumbs_name__ is not None:
                yield(resource)
            resource = resource.__parent__
    return reversed(list(gen(context)))

def crumbs_string(context):
    return ' / '.join([ p.__crumbs_name__ for p in crumbs(context) ])
