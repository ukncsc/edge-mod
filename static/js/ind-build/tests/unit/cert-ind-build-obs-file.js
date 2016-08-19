require.config({
    map: {
        'ind-build/cert-ind-build-obs-file': {
            'ind-build/cert-ind-build-viewmodel': 'ind-build/tests/unit/mock/mock-view-model',
            'ind-build/cert-ind-build-ready': 'ind-build/tests/unit/mock/mock-ready'
        }
    }
});

define([
    "knockout",
    "intern!object",
    "intern/chai!assert",
    "ind-build/tests/unit/mock/mock-abstract-mass-observable",
    "ind-build/tests/unit/mock/mock-obs-file",
    "ind-build/cert-ind-build-obs-file",
    "ind-build/tests/unit/mock/mock-view-model",
    "ind-build/indicator-builder-shim"

], function (ko, registerSuite, assert, mockMassObs, mockObsFile, CERTObservableFile, mockViewModel, indicator_builder) {
    "use strict";

    // statics go here

    return registerSuite(function () {

        // suite variables go here

        return {
            name: "ind-build/cert-ind-build-obs-file",
            "constructor": function () {
                assert.isDefined(CERTObservableFile);
                indicator_builder.vm = new mockViewModel();

            },
            "hash type": {
                "get SSDEEP": function () {
                    var obsFile = new CERTObservableFile();
                    var type = obsFile.getHashType("1234567890:0aZ/+:/+zA0,\"path/to/a.file\"");
                    assert.isTrue(type === "SSDEEP");
                },

                "get SHA224": function () {
                    var obsFile = new CERTObservableFile();
                    var type = obsFile.getHashType("12345678901234567890123456789012345678901234567890123456");
                    assert.isTrue(type === "SHA224");
                },
                "get MD5": function () {
                    var obsFile = new CERTObservableFile();
                    var type = obsFile.getHashType("12345678901234567890123456789012");
                    assert.isTrue(type === "MD5");
                },
                "get SHA1": function () {
                    var obsFile = new CERTObservableFile();
                    var type = obsFile.getHashType("1234567890123456789012345678901234567890");
                    assert.isTrue(type === "SHA1");
                },
                "get SHA256": function () {
                    var obsFile = new CERTObservableFile();
                    var type = obsFile.getHashType("1234567890123456789012345678901234567890123456789012345678901234");
                    assert.isTrue(type === "SHA256");
                },
                "get SHA384": function () {
                    var obsFile = new CERTObservableFile();
                    var type = obsFile.getHashType("123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456");
                    assert.isTrue(type === "SHA384");
                },
                "get SHA512": function () {
                    var obsFile = new CERTObservableFile();
                    var type = obsFile.getHashType("12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678");
                    assert.isTrue(type === "SHA512");
                },
                "get MD6": function () {
                    var obsFile = new CERTObservableFile();
                    var type = obsFile.getHashType("123456789012345678901234567890123456789012");
                    assert.isTrue(type === "MD6");
                },
                "get Other": function () {
                    var obsFile = new CERTObservableFile();
                    var type = obsFile.getHashType("blablabla");
                    assert.isTrue(type === "Other");
                },
                "get Other too long": function () {
                    var obsFile = new CERTObservableFile();
                    var type = obsFile.getHashType("12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678123456789012345678123456789012345678");
                    assert.isTrue(type === "Other");
                }
            },
            "validation": {
                "has an unknown hash": function () {
                    indicator_builder.vm.builderMode().isBatch = true;
                    var obsFile = new CERTObservableFile();
                    obsFile.getObjectValuesArray().push("0-1293';.safd");
                    assert.isTrue(obsFile.doValidation().hasErrors());
                },

                "has a known hash": function () {
                    indicator_builder.vm.builderMode().isBatch = true;
                    var obsFile = new CERTObservableFile();
                    obsFile.getObjectValuesArray().push("12345678901234567890123456789012345678901234567890123456");
                    assert.isFalse(obsFile.doValidation().hasErrors());
                },

                "not in batch mode": function () {
                    indicator_builder.vm.builderMode().isBatch = false;
                    var obsFile = new CERTObservableFile();
                    assert.isFalse(obsFile.doValidation().hasErrors());
                },


                "has a known hash and starts with name": function () {
                    indicator_builder.vm.builderMode().isBatch = true;
                    var obsFile = new CERTObservableFile();
                    obsFile.getObjectValuesArray().push("\'hello\';12345678901234567890123456789012345678901234567890123456");
                    assert.isFalse(obsFile.doValidation().hasErrors());
                }
            },
            "titles": {
                "title set": function () {
                    var obsFile = new CERTObservableFile();
                    obsFile.objectTitle("Hello");
                    var res = obsFile.getOrCreateTitle("", 0);
                    assert.isTrue(res === "Hello");
                },
                "title in hash": function () {
                    var obsFile = new CERTObservableFile();
                    obsFile.objectTitle("");
                    var res = obsFile.getOrCreateTitle("\"name\"", 0);
                    assert.isTrue(res === "name");
                },
                "too long for title hash set": function () {
                    var obsFile = new CERTObservableFile();
                    var res = obsFile.getOrCreateTitle("Hello123123123123123Hello123123123123123Hello123123123123123Hello123123123123123Hello123123123123123Hello123123123123123Hel", 0);
                    assert.isTrue(res === "File : Hello123123123123123Hello123123123123123Hello123123123123123Hello12312312");
                },
                "title not set hash set": function () {
                    var obsFile = new CERTObservableFile();
                    obsFile.objectTitle("");
                    var res = obsFile.getOrCreateTitle("text", 0);
                    assert.isTrue(res === "File : text");
                },
                "title not set hash and idx set": function () {
                    var obsFile = new CERTObservableFile();
                    obsFile.objectTitle("");
                    var res = obsFile.getOrCreateTitle("text", 1);
                    assert.isTrue(res === "File : text 1");
                },
                "no title no hash value": function () {
                    var obsFile = new CERTObservableFile();
                    obsFile.objectTitle("");
                    var res = obsFile.getOrCreateTitle("", 0);
                    assert.isTrue(res === "File : ");
                },
                "2 hash values": function () {
                    var obsFile = new CERTObservableFile();
                    obsFile.objectTitle("");
                    var res = obsFile.getOrCreateTitle("hash1;hash2", 0);
                    assert.isTrue(res === "File : hash1;hash2");
                }
            },

            "save": {
                "save non batch": function () {
                    var obsFile = new CERTObservableFile();
                    obsFile.objectTitle("123");
                    var res = obsFile.save(0);
                    var expectedResult = ko.toJSON({
                        "getObjectValuesArray": [],
                        "hashes": [],
                        "selected_hash": "",
                        "hash_value": "",
                        "objectTitle": "123",
                        "objectType": "File",
                        "file_name": "",
                        "file_extension": "",
                        "declaredClass": "CERTObservableFile"
                    });

                    assert.isTrue(res === expectedResult)
                },
                "bulk save non batch": function () {
                    var obsFile = new CERTObservableFile();
                    obsFile.objectTitle("123");
                    var res = obsFile.bulkSave(0)[0];
                    var expectedResult = ko.toJSON({
                        "getObjectValuesArray": [],
                        "hashes": [],
                        "selected_hash": "",
                        "hash_value": "",
                        "objectTitle": "123",
                        "objectType": "File",
                        "file_name": "",
                        "file_extension": "",
                        "declaredClass": "CERTObservableFile"
                    });

                    assert.isTrue(res === expectedResult)
                },
                "save no idx": function () {
                    var obsFile = new CERTObservableFile();
                    var precall = ko.toJSON(obsFile);
                    obsFile.save();
                    assert.isTrue(precall === ko.toJSON(obsFile))
                },
                "save hash with name": function () {
                    var obsFile = new CERTObservableFile();
                    obsFile.getObjectValuesArray().push("\'hello.txt\';12345678901234567890123456789012345678901234567890123456");
                    var res = obsFile.save(0);
                    var expectedResult = ko.toJSON({
                        "getObjectValuesArray": [],
                        "hashes": [],
                        "selected_hash": "SHA224",
                        "hash_value": "12345678901234567890123456789012345678901234567890123456",
                        "objectTitle": "hello.txt",
                        "objectType": "File",
                        "file_name": "hello.txt",
                        "file_extension": "txt",
                        "declaredClass": "CERTObservableFile"
                    });

                    assert.isTrue(res === expectedResult)
                },
                "bulk save hash with name": function () {
                    var obsFile = new CERTObservableFile();
                    obsFile.getObjectValuesArray().push("\'hello.txt\';12345678901234567890123456789012345678901234567890123456");
                    var res = obsFile.bulkSave(0)[0];
                    var expectedResult = ko.toJSON({
                        "getObjectValuesArray": [],
                        "hashes": [],
                        "selected_hash": "SHA224",
                        "hash_value": "12345678901234567890123456789012345678901234567890123456",
                        "objectTitle": "hello.txt",
                        "objectType": "File",
                        "file_name": "hello.txt",
                        "file_extension": "txt",
                        "declaredClass": "CERTObservableFile"
                    });

                    assert.isTrue(res === expectedResult)
                },
                "save hash with name no ext": function () {
                    var obsFile = new CERTObservableFile();
                    obsFile.getObjectValuesArray().push("\'hello\';12345678901234567890123456789012345678901234567890123456");
                    var res = obsFile.save(0);
                    var expectedResult = ko.toJSON({
                        "getObjectValuesArray": [],
                        "hashes": [],
                        "selected_hash": "SHA224",
                        "hash_value": "12345678901234567890123456789012345678901234567890123456",
                        "objectTitle": "hello",
                        "objectType": "File",
                        "file_name": "hello",
                        "file_extension": "",
                        "declaredClass": "CERTObservableFile"
                    });

                    assert.isTrue(res === expectedResult)
                },
                "save hash with no name": function () {
                    var obsFile = new CERTObservableFile();
                    obsFile.getObjectValuesArray().push("12345678901234567890123456789012345678901234567890123456");
                    var res = obsFile.save(0);
                    var expectedResult = ko.toJSON({
                        "getObjectValuesArray": [],
                        "hashes": [],
                        "selected_hash": "SHA224",
                        "hash_value": "12345678901234567890123456789012345678901234567890123456",
                        "objectTitle": "File : 12345678901234567890123456789012345678901234567890123456",
                        "objectType": "File",
                        "file_name": "",
                        "file_extension": "",
                        "declaredClass": "CERTObservableFile"
                    });

                    assert.isTrue(res === expectedResult)
                }
            },

            "for coverage": {
                "search": function () {
                    var obsFile = new CERTObservableFile();
                    obsFile.getSearchValue();
                },
                "load": function () {
                    var obsFile = new CERTObservableFile();
                    var precall = ko.toJSON(obsFile);
                    obsFile.load();
                    assert.isTrue(precall === ko.toJSON(obsFile))

                },
                "addHash": function () {
                    var obsFile = new CERTObservableFile();
                    var precall = ko.toJSON(obsFile);
                    obsFile.addHash();
                    assert.isTrue(precall === ko.toJSON(obsFile))
                },
                "removeHash": function () {
                    var obsFile = new CERTObservableFile();
                    var precall = ko.toJSON(obsFile);
                    obsFile.removeHash();
                    assert.isTrue(precall === ko.toJSON(obsFile))
                }
            }
        }
    });
});
