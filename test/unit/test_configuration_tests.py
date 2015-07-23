import contextlib
import pytest
from registry.app import factory
from registry.config import testing


@contextlib.contextmanager
def flag_restorer():
    has_old_flags = hasattr(testing, 'FLAGS')
    old_flags = getattr(testing, 'FLAGS', None)

    yield

    if has_old_flags:
        testing.FLAGS = old_flags
    else:
        del testing.FLAGS


def test_check_flag_without_label_raises():
    with flag_restorer():
        testing.FLAGS = {
            'fail': {
                'can_checkin': False
            }
        }

        with pytest.raises(ValueError):
            factory('registry.config.testing')


def test_check_flag_without_action_raises():
    with flag_restorer():
        testing.FLAGS = {
            'fail': {
                'label': 'fails'
            }
        }

        with pytest.raises(ValueError):
            factory('registry.config.testing')

        testing.FLAGS = {
            'fail': {
                'label': 'fails',
                'can_checkin': True
            }
        }

        with pytest.raises(ValueError):
            factory('registry.config.testing')

        testing.FLAGS = {
            'fail': {
                'label': 'fails',
                'can_checkout': True
            }
        }

        with pytest.raises(ValueError):
            factory('registry.config.testing')
