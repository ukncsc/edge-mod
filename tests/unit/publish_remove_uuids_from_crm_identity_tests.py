import unittest

from adapters.certuk_mod.publisher.publisher_edge_object import PublisherEdgeObject


class PublishRemoveIDsFromCRMIdentityTests(unittest.TestCase):

    doc_fully_populated = {
        'data':
            {'api': {
                'victims': [
                    {'id': 'pss:identity-dd66b0fd-ff3a-4468-a441-1c4b86be5101',
                     'xsi:type': 'ciqIdentity:CIQIdentity3.0InstanceType',
                     'specification':
                         {'organisation_info': {'industry_type': 'Defence'}},
                     'name': '1604f1ae-2a8c-4339-ae02-bcc0d123e892'},

                    {'id': 'pss:identity-7f859afc-cb3d-4c02-a30a-e9bfa2b4a14f',
                     'xsi:type': 'ciqIdentity:CIQIdentity3.0InstanceType',
                     'specification': {},
                     'name': '1604f1ae-2a8c-4339-ae02-bcc0d123e892'}],

                'coordinators': [
                    {'identity':
                         {'id': 'pss:identity-b605d3a6-a24d-4e05-a45b-80e6b226f562',
                          'xsi:type': 'ciqIdentity:CIQIdentity3.0InstanceType',
                          'specification': {
                              'organisation_info': {'industry_type': 'Water'}},
                          'name': '1604f1ae-2a8c-4339-ae02-bcc0d123e892'}},
                    {'identity':
                         {'id': 'pss:identity-f2359c72-d9c0-4d94-862f-c0c58a3da02e',
                          'xsi:type': 'ciqIdentity:CIQIdentity3.0InstanceType',
                          'specification': {
                              'organisation_info': {'industry_type': 'Gov'}},
                          'name': '1604f1ae-2a8c-4339-ae02-bcc0d123e892'}}],

                'reporter':
                    {'identity':
                         {'id': 'pss:identity-3c6a3891-691b-488e-adb7-5fa30ba01644',
                          'xsi:type': 'ciqIdentity:CIQIdentity3.0InstanceType',
                          'specification':
                              {'organisation_info': {'industry_type': 'Telecoms'}},
                          'name': '1604f1ae-2a8c-4339-ae02-bcc0d123e892'}},

                'responders': [
                    {'identity':
                         {'id': 'pss:identity-7fc4d715-82a8-48c6-bb2f-7afb9825cabd',
                          'xsi:type': 'ciqIdentity:CIQIdentity3.0InstanceType',
                          'specification':
                              {'organisation_info': {'industry_type': 'Public'}},
                          'name': '1604f1ae-2a8c-4339-ae02-bcc0d123e892'}}]}}}

    doc_fully_populated_returned = {
        'data':
            {'api': {
                'victims': [
                    {'id': 'pss:identity-dd66b0fd-ff3a-4468-a441-1c4b86be5101',
                     'xsi:type': 'ciqIdentity:CIQIdentity3.0InstanceType',
                     'specification':
                         {'organisation_info': {'industry_type': 'Defence'}},
                     'name': 'null:Defence'},

                    {'id': 'pss:identity-7f859afc-cb3d-4c02-a30a-e9bfa2b4a14f',
                     'xsi:type': 'ciqIdentity:CIQIdentity3.0InstanceType',
                     'specification': {},
                     'name': 'null:'}],

                'coordinators': [
                    {'identity':
                         {'id': 'pss:identity-b605d3a6-a24d-4e05-a45b-80e6b226f562',
                          'xsi:type': 'ciqIdentity:CIQIdentity3.0InstanceType',
                          'specification': {
                              'organisation_info': {'industry_type': 'Water'}},
                          'name': 'null:Water'}},
                    {'identity':
                         {'id': 'pss:identity-f2359c72-d9c0-4d94-862f-c0c58a3da02e',
                          'xsi:type': 'ciqIdentity:CIQIdentity3.0InstanceType',
                          'specification': {
                              'organisation_info': {'industry_type': 'Gov'}},
                          'name': 'null:Gov'}}],

                'reporter':
                    {'identity':
                         {'id': 'pss:identity-3c6a3891-691b-488e-adb7-5fa30ba01644',
                          'xsi:type': 'ciqIdentity:CIQIdentity3.0InstanceType',
                          'specification':
                              {'organisation_info': {'industry_type': 'Telecoms'}},
                          'name': 'null:Telecoms'}},

                'responders': [
                    {'identity':
                         {'id': 'pss:identity-7fc4d715-82a8-48c6-bb2f-7afb9825cabd',
                          'xsi:type': 'ciqIdentity:CIQIdentity3.0InstanceType',
                          'specification':
                              {'organisation_info': {'industry_type': 'Public'}},
                          'name': 'null:Public'}}]}}}

    doc_no_identity_key = {
        'data': {
            'api': {
                'victims': [
                    {'id': 'pss:identity-dd66b0fd-ff3a-4468-a441-1c4b86be5101',
                     'xsi:type': 'ciqIdentity:CIQIdentity3.0InstanceType',
                     'specification':
                         {'organisation_info': {'industry_type': 'Defence'}},
                     'name': '1604f1ae-2a8c-4339-ae02-bcc0d123e892'}
                ],
                'coordinators': [
                    {'id': 'pss:identity-b605d3a6-a24d-4e05-a45b-80e6b226f562',
                     'xsi:type': 'ciqIdentity:CIQIdentity3.0InstanceType',
                     'specification': {
                         'organisation_info': {'industry_type': 'Water'}},
                     'name': '1604f1ae-2a8c-4339-ae02-bcc0d123e892'}
                ],
                'reporter': {
                     'id': 'pss:identity-3c6a3891-691b-488e-adb7-5fa30ba01644',
                     'xsi:type': 'ciqIdentity:CIQIdentity3.0InstanceType',
                     'specification':
                         {'organisation_info': {'industry_type': 'Telecoms'}},
                     'name': '1604f1ae-2a8c-4339-ae02-bcc0d123e892'
                },
                'responders': [
                    {'id': 'pss:identity-7fc4d715-82a8-48c6-bb2f-7afb9825cabd',
                     'xsi:type': 'ciqIdentity:CIQIdentity3.0InstanceType',
                     'specification':
                         {'organisation_info': {'industry_type': 'Public'}},
                     'name': '1604f1ae-2a8c-4339-ae02-bcc0d123e892'}
                ]
            }
        }
    }

    doc_no_identity_key_returned = {
        'data': {
            'api': {
                'victims': [
                    {'id': 'pss:identity-dd66b0fd-ff3a-4468-a441-1c4b86be5101',
                     'xsi:type': 'ciqIdentity:CIQIdentity3.0InstanceType',
                     'specification':
                         {'organisation_info': {'industry_type': 'Defence'}},
                     'name': 'null:Defence'}
                ],
                'coordinators': [
                    {'id': 'pss:identity-b605d3a6-a24d-4e05-a45b-80e6b226f562',
                     'xsi:type': 'ciqIdentity:CIQIdentity3.0InstanceType',
                     'specification': {
                         'organisation_info': {'industry_type': 'Water'}},
                     'name': 'null:Water'}
                ],
                'responders': [
                    {'id': 'pss:identity-7fc4d715-82a8-48c6-bb2f-7afb9825cabd',
                     'xsi:type': 'ciqIdentity:CIQIdentity3.0InstanceType',
                     'specification':
                         {'organisation_info': {'industry_type': 'Public'}},
                     'name': 'null:Public'}
                ]
            }
        }
    }

    def test_remove_uuid_name_fully_populated(self):
        returned_doc = PublisherEdgeObject.strip_uuids_from_identities(self.doc_fully_populated)
        self.assertDictEqual(returned_doc, self.doc_fully_populated_returned)

    def test_no_identity_key_on_list_ids(self):
        returned_doc = PublisherEdgeObject.strip_uuids_from_identities(self.doc_no_identity_key)
        self.assertDictEqual(returned_doc, self.doc_no_identity_key)
