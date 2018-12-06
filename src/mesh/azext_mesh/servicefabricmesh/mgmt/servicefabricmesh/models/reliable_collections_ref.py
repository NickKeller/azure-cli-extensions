# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from msrest.serialization import Model


class ReliableCollectionsRef(Model):
    """Specifying this parameter adds support for reliable collections.

    :param name: Name of ReliableCollection resource. Right now it's not used
     and you can use any string.
    :type name: str
    :param do_not_persist_state: False (the default) if ReliableCollections
     state is persisted to disk as usual. True if you do not want to persist
     state, in which case replication is still enabled and you can use
     ReliableCollections as distributed cache.
    :type do_not_persist_state: bool
    """

    _validation = {
        'name': {'required': True},
    }

    _attribute_map = {
        'name': {'key': 'name', 'type': 'str'},
        'do_not_persist_state': {'key': 'doNotPersistState', 'type': 'bool'},
    }

    def __init__(self, name, do_not_persist_state=None):
        super(ReliableCollectionsRef, self).__init__()
        self.name = name
        self.do_not_persist_state = do_not_persist_state