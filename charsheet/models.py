from pyramid.events import NewRequest
from pyramid.events import subscriber

import pyramid.security as sec

import sqlalchemy.orm as orm
import sqlalchemy as sa

from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.collections import attribute_mapped_collection
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

Valid_User =    ('group', 'valid_user')
Admin =         ('group', 'admin')
Active_Admin =  ('group', 'active_admin')

ALLOW_ACTIVE_ADMIN =  (sec.Allow, Active_Admin, sec.ALL_PERMISSIONS)

class Root(object):
    __name__ = None
    __parent__ = None
    __acl__ = [
            ALLOW_ACTIVE_ADMIN,
            (sec.Allow, Valid_User, 'basic'),
            (sec.Deny, sec.Authenticated, 'basic'),
            (sec.Allow, sec.Everyone, 'basic'),
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
            (sec.Allow, Admin, sec.ALL_PERMISSIONS),
            (sec.Allow, Valid_User, 'view'),
            ]

    __crumbs_name__ = 'User List'

    def __getitem__(self,key):
        try:
            return db.query(User).filter(User.name == key).one()
        except NoResultFound:
            raise KeyError(key)

class UserRegister(object):
    __acl__ = [
            (sec.Deny, Valid_User, sec.ALL_PERMISSIONS),
            (sec.Allow, sec.Authenticated, 'add'),
            sec.DENY_ALL,
            ]

    __crumbs_name__ = 'Register'

class PartyList(object):
    __acl__ = [
            (sec.Allow, Valid_User, 'view'),
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
        return [(sec.Allow, self.email, ('view','edit','delete'))]

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
        groups = [Valid_User]
        if self.admin:
            groups.append(Admin)
        if self.active_admin:
            groups.append(Active_Admin)
        return groups

class Party(Base):
    __tablename__ = 'party'
    __parent__ = partylist

    @property
    def __name__(self):
        return self.name

    @property
    def __acl__(self):
        acl = [(
            sec.Allow,
            perm.user.email,
            perm.edit and ('view','edit','delete','add') or 'view',
            ) for perm in self.permissions ]

        acl += [(
            sec.Allow,
            perm.user.email,
            'view',
            ) for perm in char.permissions for char in self.characters ]

        acl.append(ALLOW_ACTIVE_ADMIN)
        acl.append(sec.DENY_ALL)

        return acl

    @property
    def __crumbs_name__(self):
        return self.name

    @classmethod
    def every(cls):
        return db.query(cls).order_by(cls.name)

    def __getitem__(self,key):
        return self.characters[key]

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

    active = sa.Column(
            sa.Boolean(name='active'),
            nullable=False,
            default=True,
            )

    characters = orm.relationship(
            'Character',
            backref=orm.backref(
                'party',
                lazy='joined',
                ),
            collection_class=attribute_mapped_collection('name'),
            cascade="all, delete-orphan",
            passive_deletes=True,
            )

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
        acl = [(
            sec.Allow,
            perm.user.email,
            perm.edit and ('view','edit') or 'view',
            ) for perm in self.permissions ]

        if self.private:
            # Move in GM permissions from party
            acl += [(
                sec.Allow,
                perm.user.email,
                ('view','edit','delete','add'),
                ) for perm in self.permissions if perm.edit ]
            # Deny everything else.
            acl.append(ALLOW_ACTIVE_ADMIN)
            acl.append(sec.DENY_ALL)

        return acl

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

    party_id = sa.Column(
            sa.ForeignKey(
                'party.id',
                ondelete='CASCADE',
                onupdate='CASCADE',
                ),
            nullable=False,
            )

    name = sa.Column(
            sa.String(length=20),
            nullable=False,
            )

    private = sa.Column(
            sa.Boolean(name='private'),
            nullable=False,
            default=False,
            )

class PartyPermission(Base):
    __tablename__ = 'party_permission'

    __table_args__ = (
            sa.PrimaryKeyConstraint('party_id', 'user_id'),
            )

    party_id = sa.Column(
            sa.ForeignKey(
                'party.id',
                ondelete='CASCADE',
                onupdate='CASCADE',
                ),
            nullable=False,
            )

    user_id = sa.Column(
            sa.ForeignKey(
                'user.id',
                ondelete='CASCADE',
                onupdate='CASCADE',
                ),
            nullable=False,
            )

    edit = sa.Column(
            sa.Boolean(name='edit'),
            nullable=False,
            default=False,
            )

    party = orm.relationship(
            'Party',
            backref=orm.backref(
                'permissions',
                cascade="all, delete-orphan",
                passive_deletes=True,
                ),
            lazy='joined',
            innerjoin=True,
            )

    user = orm.relationship(
            'User',
            backref=orm.backref(
                'party_permissions',
                cascade="all, delete-orphan",
                passive_deletes=True,
                ),
            lazy='joined',
            innerjoin=True,
            )

class CharacterPermission(Base):
    __tablename__ = 'character_permission'

    __table_args__ = (
            sa.PrimaryKeyConstraint('character_id', 'user_id'),
            )

    character_id = sa.Column(
            sa.ForeignKey(
                'character.id',
                ondelete='CASCADE',
                onupdate='CASCADE',
                ),
            nullable=False,
            )

    user_id = sa.Column(
            sa.ForeignKey(
                'user.id',
                ondelete='CASCADE',
                onupdate='CASCADE',
                ),
            nullable=False,
            )

    edit = sa.Column(
            sa.Boolean(name='edit'),
            nullable=False,
            default=False,
            )

    character = orm.relationship(
            'Character',
            backref=orm.backref(
                'permissions',
                lazy='subquery',
                cascade="all, delete-orphan",
                passive_deletes=True,
                ),
            lazy='joined',
            innerjoin=True,
            )
    user = orm.relationship('User',
            backref=orm.backref(
                'character_permissions',
                cascade="all, delete-orphan",
                passive_deletes=True,
                ),
            lazy='joined',
            innerjoin=True,
            )


def get_root(request):
    return root

@sa.event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

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
