from uuid import uuid4
import pytest
from flask import url_for
from registry.extensions import db
from registry.models import Group, Passport, commit_model
from registry.utils import pass_spec_parser


@pytest.fixture
def group_factory():
    def factory(name, pass_id_base, num_passes=3):
        group = commit_model(Group, name=name)

        for i in range(num_passes):
            commit_model(Passport, surname='John %d' % i,
                         name='Doe %d' % i, pass_id=pass_id_base + i,
                         group=group, phone='123', age=14)

        return group
    return factory


@pytest.fixture
def group(request):
    return {
        'name': 'KiKaKo'
    }


GROUP_REQUIREMENTS = {
    None: False,
    'name': True
}


@pytest.fixture(params=GROUP_REQUIREMENTS.items())
def requirement(request):
    return request.param


@pytest.fixture(params=['check_in', 'check_out'])
def transaction(request):
    return request.param


@pytest.fixture(params=[None, 2])
def transaction_skip(request):
    return request.param


GROUP_PASSES = [
    {
        'set': '111',
        'success': True
    }, {
        'set': '111,112',
        'success': True
    }, {
        'set': '111, 112',
        'success': True
    }, {
        'set': '111-113',
        'success': True
    }, {
        'set': '111 - 113',
        'success': True
    }, {
        'set': '111,113-115',
        'success': True
    }, {
        'set': '111-113',
        'success': False,
        'other': [111]
    }, {
        'pre': [112, 114],
        'set': '111-115',
        'success': False,
        'other': [111, 113]
    }
]


@pytest.fixture(params=GROUP_PASSES)
def pass_range_specification(request):
    return request.param


def test_index_shows_groups(app, group_factory):
    client = app.test_client()
    with app.test_request_context():
        groupA = group_factory('Group A', 111)
        groupB = group_factory('Group B', 222)
        url = url_for('group.index')
        r = client.get(url)

        assert r.status_code == 200
        body = r.data.decode('utf-8')
        assert body.find(groupA.name) != -1
        assert body.find(groupB.name) != -1


def test_group_creation(app, group, requirement):
    key, required = requirement
    client = app.test_client()
    with app.test_request_context():
        post_url = url_for('group.new')
        if required:
            expected_url = url_for('group.new', _external=True)
            expected_status_code = 406
        else:
            expected_url = url_for('group.index', _external=True)
            expected_status_code = 302

        group.pop(key, None)
        r = client.post(post_url, data=group)

        assert r.status_code == expected_status_code
        if not required:
            assert r.headers.get('Location') == expected_url


def test_group_creation_unique_name(app, group):
    client = app.test_client()
    with app.test_request_context():
        commit_model(Group, name='Group A')
        post_url = url_for('group.new')
        group['name'] = 'Group A'
        r = client.post(post_url, data=group)

        assert r.status_code == 406


def test_edit_non_existing_group_returns_404(app):
    client = app.test_client()
    with app.test_request_context():
        url = url_for('group.edit', group_id=str(uuid4()))
        r = client.get(url)

        assert r.status_code == 404


def test_group_edit(app):
    client = app.test_client()
    with app.test_request_context():
        group = commit_model(Group, name='Group A')
        url = url_for('group.edit', group_id=group.id)

        r = client.get(url)
        assert r.status_code == 200

        r = client.post(url, data=dict(name='Group A2'))
        assert r.status_code == 302
        assert r.headers.get('Location') == url_for('group.index',
                                                    _external=True)

        db.session.expire_all()

        assert Group.query.get(group.id).name == 'Group A2'


def test_add_passes_to_group(app, pass_range_specification):
    _set = pass_range_specification['set']
    other = pass_range_specification.get('other', [])
    pre = pass_range_specification.get('pre', [])
    client = app.test_client()
    with app.test_request_context():
        group = commit_model(Group, name='Group A')
        other_group = commit_model(Group, name='Other Group')
        existing_passes = []
        for pass_id in other:
            # Put some passes in other group
            commit_model(Passport, surname='John', name='Doe', pass_id=pass_id,
                         group=other_group, phone='123', age=14)
            existing_passes.append(pass_id)

        wanted_passes = pass_spec_parser(_set)
        for pass_id in wanted_passes:
            # Create remaining passes
            if pass_id in existing_passes:
                continue
            _group = group if pass_id in pre else None
            commit_model(Passport, surname='New John', name='Doe',
                         pass_id=pass_id, phone='123', age=14, group=_group)

        # Set passes on original group
        url = url_for('group.edit', group_id=group.id)
        data = dict(name=group.name, passport_ids=_set)
        r = client.post(url, data=data)

        db.session.expire_all()

        success = pass_range_specification['success']
        assert r.status_code == (302 if success else 406)
        group = Group.query.get(group.id)
        passes = sorted([passport.pass_id for passport in group.passports])
        if success:
            assert passes == pass_spec_parser(_set)
        else:
            assert passes == pre


def _create_passes(pass_ids, group_name):
    group = Group(name=group_name)
    for pass_id in pass_ids:
        p = Passport(surname='New John', name='Doe', pass_id=pass_id,
                     phone='123', age=14, group=group)
        db.session.add(p)
    db.session.commit()
    return group


def test_group_transaction(app, transaction, transaction_skip):
    client = app.test_client()
    with app.test_request_context():
        passport_ids = [1, 2, 3]
        group = _create_passes(passport_ids, 'Test')

        if 'check_out' == transaction:
            for passport in group.passports:
                passport.check_in(commit=False)
            db.session.commit()
        db.session.expire_all()

        pass_ids = [pass_id for pass_id in passport_ids
                    if pass_id != transaction_skip]
        data = dict(passports=pass_ids)
        url = url_for('group.%s' % transaction, group_id=group.id)
        r = client.post(url, data=data)

        assert r.status_code == 302
        db.session.expire_all()

        group = Group.query.get(group.id)
        mode = (True if 'check_in' == transaction else False)
        for passport in group.passports:
            if passport.pass_id in pass_ids:
                assert passport.checked_in is mode
            else:
                assert passport.checked_in is not mode
