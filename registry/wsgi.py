import os
from registry.app import factory


if 'REGISTRY_CONFIG_MODULE' not in os.environ:
    raise RuntimeError('No REGISTRY_CONFIG_MODULE environment set.')

application = factory(os.environ['REGISTRY_CONFIG_MODULE'])
