from pyramid.events import NewRequest
from pyramid.events import subscriber
from pyramid.security import Allow
from pyramid.security import ALL_PERMISSIONS
from pyramid.security import Authenticated
from pyramid.security import Deny
from pyramid.security import DENY_ALL
from pyramid.security import Everyone

import sqlalchemy as sa
import sqlalchemy.orm as orm

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound

db = orm.scoped_session(orm.sessionmaker())

@subscriber(NewRequest)
def begin_session(event):
    def end_session(request):
        db.remove()
    event.request.add_finished_callback(end_session)

Base = declarative_base()

Base.metadata.naming_convention = {
    'ix': 'ix_%(column_0_label)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(constraint_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'pk': 'pk_%(table_name)s'
    }

class Root(object):
    __name__ = None
    __parent__ = None
    __acl__ = [
            (Allow, 'group:active_admin', ('view','edit','add','delete','admin')),
            (Allow, 'group:validuser', 'basic'),
            (Deny, Authenticated, 'basic'),
            (Allow, Everyone, 'basic'),
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
            (Allow, 'group:admin', ('view','edit','add','delete','admin')),
            (Allow, 'group:validuser', 'view'),
            ]

    __crumbs_name__ = 'User List'

    def __getitem__(self,key):
        try:
            return db.query(User).filter(User.name == key).one()
        except NoResultFound:
            raise KeyError(key)

class UserRegister(object):
    __acl__ = [
            (Deny, 'group:validuser', ALL_PERMISSIONS),
            (Allow, Authenticated, 'add'),
            DENY_ALL,
            ]

    __crumbs_name__ = 'Register'

class PartyList(object):
    __acl__ = [
            (Allow, 'group:validuser', 'view'),
            ]

    __crumbs_name__ = 'Party List'

    def __getitem__(self,key):
        try:
            return db.query(Party).filter(Party.name == key).one()
        except NoResultFound:
            raise KeyError(key)

root = Root()

userlist = UserList()
root.add('user',userlist)

partylist = PartyList()
root.add('party',partylist)

userregister = UserRegister()
root.add('register',userregister)

class User(Base):
    __tablename__ = 'user'

    __parent__ = userlist

    @property
    def __name__(self):
        return self.name

    @property
    def __acl__(self):
        return [(Allow, self.email, ('view','edit','delete'))]

    @property
    def __crumbs_name__(self):
        return self.name

    @classmethod
    def every(cls): 
        return db.query(cls).order_by(cls.name)

    id = sa.Column(
            sa.Integer,
            primary_key=True,
            )

    name = sa.Column(
            sa.String(length=20),
            nullable=False,
            index=True,
            unique=True,
            )

    email = sa.Column(
            sa.String(length=300),
            nullable=False,
            index=True,
            unique=True,
            )

    admin = sa.Column(
            sa.Boolean(name='admin'),
            nullable=False,
            default=False,
            )

    active_admin = sa.Column(
            sa.Boolean(name='active_admin'),
            nullable=False,
            default=False,
            )

    def groups(self):
        groups = ['group:validuser']
        if self.admin:
            groups.append('group:admin')
        if self.active_admin:
            groups.append('group:active_admin')
        return groups

class Party(Base):
    __tablename__ = 'party'
    __parent__ = partylist

    @property
    def __name__(self):
        return self.name

    @property
    def __acl__(self):
        return []

    @property
    def __crumbs_name__(self):
        return self.name

    @classmethod
    def every(cls):
        return db.query(cls).order_by(cls.name)

    def __getitem__(self,key):
        try:
            return db.query(Character).filter(and_(
                Character.party_id == self.id,
                Character.name == key,
                )).one()
        except NoResultFound:
            raise KeyError(key)

    id = sa.Column(
            sa.Integer,
            primary_key=True,
            )

    name = sa.Column(
            sa.String(length=20),
            nullable=False,
            index=True,
            unique=True,
            )

    characters = orm.relationship('Character', backref='party')

class PartyPermission(Base):
    __tablename__ = 'party_permission'

    __table_args__ = (
            sa.PrimaryKeyConstraint('party_id', 'user_id'),
            )

    party_id = sa.Column(
            sa.ForeignKey('party.id'),
            nullable=False,
            )

    user_id = sa.Column(
            sa.ForeignKey('user.id'),
            nullable=False,
            )

    edit = sa.Column(
            sa.Boolean(name='edit'),
            nullable=False,
            default=False,
            )

    party = orm.relationship('Party', backref='permissions')
    user = orm.relationship('User', backref='party_permissions')


class Character(Base):
    __tablename__ = 'character'

    @property
    def __parent__(self):
        return self.party

    @property
    def __name__(self):
        return self.name

    @property
    def __acl__(self):
        return []

    @property
    def __crumbs_name__(self):
        return self.name

    __table_args__ = (
            sa.Index(
                'ix_character_party_name',
                'party_id', 'name',
                unique=True,
                ),
            )

    id = sa.Column(
            sa.Integer,
            primary_key=True,
            )

    name = sa.Column(
            sa.String(length=20),
            nullable=False,
            )

    party_id = sa.Column(
            sa.ForeignKey('party.id'),
            nullable=False,
            )

class CharacterPermission(Base):
    __tablename__ = 'character_permission'

    __table_args__ = (
            sa.PrimaryKeyConstraint('character_id', 'user_id'),
            )

    character_id = sa.Column(
            sa.ForeignKey('character.id'),
            nullable=False,
            )

    user_id = sa.Column(
            sa.ForeignKey('user.id'),
            nullable=False,
            )

    edit = sa.Column(
            sa.Boolean(name='edit'),
            nullable=False,
            default=False,
            )

    character = orm.relationship('Character', backref='permissions')
    user = orm.relationship('User', backref='character_permissions')


def get_root(request):
    return root

@subscriber(NewRequest)
def setup_user(event):
    # Run authentication
    event.request.authenticated_userid
    # If authentication fails, get_group is never run and request.user is never set.
    # Therefore; do it here!
    try:
        event.request.user
    except AttributeError:
        event.request.user = None

def get_groups(userid, request):
    try:
        user = request.user
    except AttributeError:
        user = request.user = db.query(User).filter(User.email == userid).first()

    if request.user is None:
        return []
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
