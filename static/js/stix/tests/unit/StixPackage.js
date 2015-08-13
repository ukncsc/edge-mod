define([
    "intern!object",
    "intern/chai!assert",
    "stix/StixPackage",
    "intern/dojo/text!./data/COA_package_01.json"
], function (registerSuite, assert, StixPackage, package01) {
    "use strict";

    // statics go here
    var packageData = Object.freeze({
        "purple-secure-systems:coa-00000000-0000-0000-0000-000000000000": Object.freeze({}),
        "purple-secure-systems:coa-f30bc9fa-c5ce-4e8a-800f-4411cbce2f30": Object.freeze(JSON.parse(package01))
    });

    return registerSuite(function () {

        // suite variables go here
        var classUnderTest = null;

        function loadPackage(/*String*/ packageId, /*String?*/ rootId) {
            classUnderTest = new StixPackage(packageData[packageId], rootId || packageId);
        }

        return {
            name: "stix/StixPackage",
            "no package": function () {
                assert.throws(
                    function () {
                        loadPackage(
                            "",
                            "invalid"
                        );
                    },
                    "STIX package cannot be null or undefined"
                );
            },
            "invalid id": function () {
                assert.throws(
                    function () {
                        loadPackage(
                            "purple-secure-systems:coa-00000000-0000-0000-0000-000000000000",
                            "invalid"
                        );
                    },
                    "Unable to derive type from id: invalid"
                );
            },
            "unknown type": function () {
                assert.throws(
                    function () {
                        loadPackage(
                            "purple-secure-systems:coa-00000000-0000-0000-0000-000000000000",
                            "purple-secure-systems:badtype-00000000-0000-0000-0000-000000000000"
                        );
                    },
                    "Unknown type: badtype"
                );
            },
            "rootId not found (empty package)": function () {
                assert.throws(
                    function () {
                        loadPackage(
                            "purple-secure-systems:coa-00000000-0000-0000-0000-000000000000",
                            "purple-secure-systems:coa-11111111-0000-0000-0000-000000000000"
                        );
                    },
                    "Object not found with id: purple-secure-systems:coa-11111111-0000-0000-0000-000000000000"
                );
            },
            "rootId not found (not in package)": function () {
                assert.throws(
                    function () {
                        loadPackage(
                            "purple-secure-systems:coa-f30bc9fa-c5ce-4e8a-800f-4411cbce2f30",
                            "purple-secure-systems:coa-11111111-0000-0000-0000-000000000000"
                        );
                    },
                    "Object not found with id: purple-secure-systems:coa-11111111-0000-0000-0000-000000000000"
                );
            },
            "valid package": {
                setup: function () {
                    loadPackage("purple-secure-systems:coa-f30bc9fa-c5ce-4e8a-800f-4411cbce2f30");
                },
                "returns non-null": function () {
                    assert.isNotNull(classUnderTest.root);
                },
                "has correct id": function () {
                    assert.equal(classUnderTest.root.id(), "purple-secure-systems:coa-f30bc9fa-c5ce-4e8a-800f-4411cbce2f30");
                }
                // TODO: safeGet, safeArrayGet, safeListGet and safeReferenceArrayGet
            }
        }
    });
});

