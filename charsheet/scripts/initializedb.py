import os
import sys

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from ..models import (
    db,
    Base,
    User,
    Party,
    Character,
    PartyPermission,
    CharacterPermission,
    )

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    engine = engine_from_config(settings, 'sqlalchemy.')
    db.configure(bind=engine)
    Base.metadata.create_all(engine)

    db.add(User(name='ankaan', email='ankan@a'))
    db.add(User(name='ankaan0', email='0@a'))
    db.add(User(name='ankaan1', email='1@a'))
    db.add(User(name='ankaan2', email='2@a'))
    db.add(User(name='ankaan4', email='4@a'))

    other = User(name='test', email='test@test.test')
    db.add(other)

    me = User(name='Ankan', email='ankaan@gmail.com', admin=True, active_admin=True)
    db.add(me)

    party = Party(name='Adventure Time')
    party.permissions.append(PartyPermission(user=me))
    db.add(party)

    charparty = Party(name='Avataria')
    char = Character(name='My Avatar', party=charparty)
    char.permissions.append(CharacterPermission(user=me))
    db.add(charparty)

    otherparty = Party(name='Not Mine')
    otherparty.permissions.append(PartyPermission(user=other))
    db.add(otherparty)

    db.commit()
