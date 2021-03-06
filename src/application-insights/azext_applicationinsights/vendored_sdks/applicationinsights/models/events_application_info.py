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


class EventsApplicationInfo(Model):
    """Application info for an event result.

    :param version: Version of the application
    :type version: str
    """

    _attribute_map = {
        'version': {'key': 'version', 'type': 'str'},
    }

    def __init__(self, **kwargs):
        super(EventsApplicationInfo, self).__init__(**kwargs)
        self.version = kwargs.get('version', None)
