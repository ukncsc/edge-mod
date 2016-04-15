import unittest
import mock
from adapters.certuk_mod.validation.common.structure import (
    ObservableStructureConverter,
    IndicatorStructureConverter,
    OtherStructureConverter
)


class ObservableStructureConverterTests(unittest.TestCase):
    OBSERVABLE_TYPES = {
        'Address': 'AddressObjectType',
        'Hostname': 'HostnameObjectType',
        'URI': 'URIObjectType',
        'Domain Name': 'DomainNameObjectType',
        'File': 'FileObjectType',
        'Mutex': 'MutexObjectType',
        'Socket': 'SocketAddressObjectType',
        'Registry Key': 'WindowsRegistryKeyObjectType',
        'Artifact': 'ArtifactObjectType',
        'Email': 'EmailMessageObjectType'
    }

    OBSERVABLE_CUSTOM_BUILDER_STRUCTURES = {
        'ArtifactObjectType': {
            'objectType': 'Artifact',
            'artifactType': 'blah',
            'artifactRaw': 'blah blah',
            'description': 'Hello'
        },

        'FileObjectType': {
            'objectType': 'File',
            'hashes': [
                {
                    'hash_type': 'MD5',
                    'hash_value': 'dummy md5'
                }
            ],
            'file_name': 'name',
            'device_path': 'C:\\',
            'full_path': 'C:\\temp',
            'file_extension': '.jpg',
            'file_format': 'JPEG',
            'size_in_bytes': '46250',
            'description': 'Hello'
        }
    }

    OBSERVABLE_CUSTOM_SIMPLE_STRUCTURES = {
        'ArtifactObjectType': {
            'object_type': 'ArtifactObjectType',
            'type': 'blah',
            'raw_artifact': 'blah blah',
            'description': 'Hello'
        },
        'FileObjectType': {
            'object_type': 'FileObjectType',
            'hashes': [
                {
                    'type': 'MD5',
                    'simple_hash_value': 'dummy md5'
                }
            ],
            'file_name': 'name',
            'device_path': 'C:\\',
            'full_path': 'C:\\temp',
            'file_extension': '.jpg',
            'file_format': 'JPEG',
            'size_in_bytes': '46250',
            'description': 'Hello'
        }
    }

    GENERIC_OBSERVABLE_STRUCTURES = {
        'BUILDER': {
            'objectType': 'Dummy',
            'field_0': 'hello'
        },
        'PACKAGE': {
            'xsi:type': 'DummyObjectType',
            'field_0': 'hello'
        },
        'SIMPLE': {
            'object_type': 'DummyObjectType',
            'field_0': 'hello'
        }
    }

    def test_BuilderToSimple_AnyValidShorthandType_GetsCorrectFullType(self):
        with mock.patch.object(ObservableStructureConverter,
                               '_ObservableStructureConverter__get_builder_package_conversion_handler',
                               return_value=None):
            for type_ in self.OBSERVABLE_TYPES:
                simple = ObservableStructureConverter.builder_to_simple(type_, {})
                self.assertEqual(simple.get('object_type'), self.OBSERVABLE_TYPES[type_])

    def test_BuilderToSimple_CustomTypes_GetCorrectStructure(self):
        for type_ in self.OBSERVABLE_CUSTOM_BUILDER_STRUCTURES:
            builder_dict = self.OBSERVABLE_CUSTOM_BUILDER_STRUCTURES[type_]
            simple = ObservableStructureConverter.builder_to_simple(builder_dict.get('objectType'), builder_dict)
            self.assertDictEqual(simple, self.OBSERVABLE_CUSTOM_SIMPLE_STRUCTURES[type_])

    def test_BuilderToSimple_GenericTypes_GetCorrectStructure(self):
        builder_dict = self.GENERIC_OBSERVABLE_STRUCTURES['BUILDER']
        simple = ObservableStructureConverter.builder_to_simple(builder_dict.get('objectType'), builder_dict)
        self.assertDictEqual(simple, self.GENERIC_OBSERVABLE_STRUCTURES['SIMPLE'])

    def test_PackageToSimple_AddressType_GetCorrectStructure(self):
        address_package = {
            'xsi:type': 'AddressObjectType',
            'category': 'ipv4-addr',
            'address_value': {
                'value': '192.168.0.1'
            }
        }
        simple = ObservableStructureConverter.package_to_simple(address_package['xsi:type'], address_package)
        self.assertDictEqual(simple, {
            'xsi:type': 'AddressObjectType',
            'category': 'ipv4-addr',
            'address_value': '192.168.0.1'
        })

    def test_PackageToSimple_SocketType_GetCorrectStructure(self):
        socket_package = {
            'xsi:type': 'SocketAddressObjectType',
            'port': {
                'port_value': '1234',
                'layer4_protocol': 'blah'
            },
            'ip_address': {
                'address_value': '102.12.211.6'
            },
            'hostname': {
                'hostname_value': 'blah'
            }
        }
        simple = ObservableStructureConverter.package_to_simple(socket_package['xsi:type'], socket_package)
        self.assertDictEqual(simple, {
            'xsi:type': 'SocketAddressObjectType',
            'port': '1234',
            'protocol': 'blah',
            'ip_address': '102.12.211.6',
            'hostname': 'blah'
        })

    def test_PackageToSimple_HTTPSessionType_GetCorrectStructure(self):
        http_sessions = [
            {
                'INPUT': {
                    'xsi:type': 'HTTPSessionObjectType',
                    'http_request_response': [
                        {
                            'http_client_request': {
                                'http_request_header': {
                                    'parsed_header': {
                                        'user_agent': 'Mozilla/5.0'
                                    }
                                }
                            }
                        }
                    ]
                },
                'OUTPUT': {
                    'xsi:type': 'HTTPSessionObjectType',
                    'user_agent': 'Mozilla/5.0'
                }
            },
            {
                'INPUT': {
                    'xsi:type': 'HTTPSessionObjectType'
                },
                'OUTPUT': {
                    'xsi:type': 'HTTPSessionObjectType',
                    'user_agent': None
                }
            }
        ]
        for session in http_sessions:
            simple = ObservableStructureConverter.package_to_simple(session['INPUT']['xsi:type'], session['INPUT'])
            self.assertDictEqual(simple, session['OUTPUT'])

    def test_PackageToSimple_flattenPropertyValueField(self):
        self.assertEqual(ObservableStructureConverter.flatten_property_value_field(
                {'value': 'abc', 'test': 'def'}), 'abc')

        self.assertEqual(ObservableStructureConverter.flatten_property_value_field('abc'), 'abc')

        self.assertEqual(ObservableStructureConverter.flatten_property_value_field(
                {'value': 123, 'test': 'def'}), 123)

        self.assertEqual(ObservableStructureConverter.flatten_property_value_field(123), 123)

        self.assertEqual(ObservableStructureConverter.flatten_property_value_field(
                {'value': {'result':'132'}, 'test': 'def'}), {'result':'132'})

        self.assertEqual(ObservableStructureConverter.flatten_property_value_field(123), 123)

        self.assertEqual(ObservableStructureConverter.flatten_property_value_field(['abc']), ['abc'])

        self.assertEqual(ObservableStructureConverter.flatten_property_value_field(None), None)

        self.assertEqual(ObservableStructureConverter.flatten_property_value_field(
                {'test2': 'abc', 'test': 'def'}), {'test2': 'abc', 'test': 'def'})

    def test_PackageToSimple_EmailType_GetCorrectStructure(self):
        email_package = {
            'xsi:type': 'EmailMessageObjectType',
            'header': {
                'subject': 'blah',
                'from': {
                    'address_value': 'someone@test.com'
                },
                'date': 'Today',
                'to': [
                    {
                        'address_value': {'value': 'test@test.com'}
                    }
                ],
                'cc': [
                    {
                        'address_value': 'mr.test@abc.co.uk'
                    },
                    {
                        'address_value': 'everyone@theworld.com'
                    }
                ]
            }
        }
        simple = ObservableStructureConverter.package_to_simple(email_package['xsi:type'], email_package)
        self.assertDictEqual(simple, {
            'xsi:type': 'EmailMessageObjectType',
            'subject': 'blah',
            'from': 'someone@test.com',
            'date': 'Today',
            'to': [
                'test@test.com'
            ],
            'cc': [
                'mr.test@abc.co.uk',
                'everyone@theworld.com'
            ],
            'bcc': None
        })

    def test_PackageToSimple_GenericTypes_GetCorrectStructure(self):
        package_dict = self.GENERIC_OBSERVABLE_STRUCTURES['PACKAGE']
        simple = ObservableStructureConverter.package_to_simple(package_dict.get('xsi:type'), package_dict)
        self.assertDictEqual(simple, self.GENERIC_OBSERVABLE_STRUCTURES['PACKAGE'])


class IndicatorStructureConverterTests(unittest.TestCase):
    def test_PackageToSimple_AllInfoInIndicator_ReturnsCorrectStructure(self):
        indicator = {
            'confidence': {
                'value': {
                    'value': 'High'
                }
            },
            'kill_chain_phases': {
                'kill_chain_phases': [
                    {
                        'phase_id': 'What a long-winded structure'
                    }
                ]
            },
            'handling': [
                {
                    'marking_structures': [
                        {
                            'color': 'RED'
                        }
                    ]
                }
            ],
            'suggested_coas': {
                'suggested_coas': [
                    'blah',
                    'blah blah'
                ]
            },
            'title': 'Hello',
            'description': 'blah',
            'short_description': 'hi'
        }
        simple = IndicatorStructureConverter.package_to_simple(indicator, {})
        self.assertDictEqual(simple, {
            'confidence': 'High',
            'phase_id': 'What a long-winded structure',
            'tlp': 'RED',
            'suggested_coas': [
                'blah',
                'blah blah'
            ],
            'title': 'Hello',
            'description': 'blah',
            'short_description': 'hi',
            'handling': [
                {
                    'marking_structures': [
                        {
                            'color': 'RED'
                        }
                    ]
                }
            ]
        })

    def test_PackageToSimple_TLPInPackageHeader_ReturnsCorrectStructure(self):
        indicator = {
            'confidence': {
                'value': {
                    'value': 'High'
                }
            },
            'kill_chain_phases': {
                'kill_chain_phases': [
                    {
                        'phase_id': 'What a long-winded structure'
                    }
                ]
            },
            'suggested_coas': {
                'suggested_coas': [
                    'blah',
                    'blah blah'
                ]
            },
            'title': 'Hello',
            'description': 'blah',
            'short_description': 'hi'
        }
        package_header = {
            'handling': [
                {
                    'marking_structures': [
                        {
                            'color': 'RED'
                        }
                    ]
                }
            ]
        }
        simple = IndicatorStructureConverter.package_to_simple(indicator, package_header)
        self.assertDictEqual(simple, {
            'confidence': 'High',
            'phase_id': 'What a long-winded structure',
            'tlp': 'RED',
            'suggested_coas': [
                'blah',
                'blah blah'
            ],
            'title': 'Hello',
            'description': 'blah',
            'short_description': 'hi'
        })

    def test_PackageToSimple_NestedStructuresMissing_ReturnsCorrectStructure(self):
        indicator = {
            'title': 'Hello',
            'description': 'blah',
            'short_description': 'hi'
        }
        simple = IndicatorStructureConverter.package_to_simple(indicator, {})
        self.assertDictEqual(simple, {
            'confidence': None,
            'phase_id': None,
            'tlp': None,
            'suggested_coas': None,
            'title': 'Hello',
            'description': 'blah',
            'short_description': 'hi'
        })

    def test_BuilderToSimple_WhenCalled_ReturnsCorrectStructure(self):
        indicator = {
            'indicatorType': 'IP Watchlist',
            'observables': [
                'blah'
            ],
            'kill_chain_phase': 'blah blah',
            'title': 'Hello',
            'description': 'blah',
            'short_description': 'hi'
        }
        simple = IndicatorStructureConverter.builder_to_simple(indicator)
        self.assertDictEqual(simple, {
            'indicator_types': 'IP Watchlist',
            'observable': [
                'blah'
            ],
            'phase_id': 'blah blah',
            'title': 'Hello',
            'description': 'blah',
            'short_description': 'hi'
        })


class OtherStructureConverterTests(unittest.TestCase):
    def test_PackageToSimple_TLPInObject_ReturnsCorrectTLP(self):
        object_ = {
            'handling': [
                {
                    'marking_structures': [
                        {
                            'color': 'RED'
                        }
                    ]
                }
            ]
        }
        simple = OtherStructureConverter.package_to_simple(object_, {})
        self.assertDictEqual(simple, {
            'tlp': 'RED',
            'handling': [
                {
                    'marking_structures': [
                        {
                            'color': 'RED'
                        }
                    ]
                }
            ]
        })

    def test_PackageToSimple_TLPInPackageHeader_ReturnsCorrectTLP(self):
        object_ = {}
        package_header = {
            'handling': [
                {
                    'marking_structures': [
                        {
                            'color': 'RED'
                        }
                    ]
                }
            ]
        }
        simple = OtherStructureConverter.package_to_simple(object_, package_header)
        self.assertDictEqual(simple, {
            'tlp': 'RED'
        })

    def test_PackageToSimple_NoTLP_ReturnsCorrectTLP(self):
        object_ = {}
        package_header = {}
        simple = OtherStructureConverter.package_to_simple(object_, package_header)
        self.assertDictEqual(simple, {
            'tlp': None
        })
