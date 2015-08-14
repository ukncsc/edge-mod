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
    var simpleObject = Object.freeze({
        prop1: "value1",
        prop2: [
            "One", "Two"
        ],
        sub1: {
            sub1prop1: [
                "Alpha", "Beta"
            ],
            sub1prop2: [
                {name: "first", value: "One"},
                {name: "second", value: "Two"}
            ],
            sub1sub: {
                sub1subprop1: "sub1subvalue1",
                sub1subprop2: "sub1subvalue2"
            }
        },
        sub2: [
            {name: "alpha", value: "Hello"},
            {name: "beta", value: "World"}
        ]
    });

    function passthrough(item) {
        return item;
    }

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
            },
            "safeGet()": {
                setup: function () {
                    loadPackage("purple-secure-systems:coa-f30bc9fa-c5ce-4e8a-800f-4411cbce2f30");
                },
                "not found returns null": function () {
                    assert.isNull(classUnderTest.safeGet(simpleObject, "bad.property.name"));
                },
                "simple property path returns value": function () {
                    assert.equal(classUnderTest.safeGet(simpleObject, "prop1"), "value1");
                },
                "compound property path returns value": function () {
                    assert.equal(classUnderTest.safeGet(simpleObject, "sub1.sub1sub.sub1subprop1"), "sub1subvalue1");
                }
            },
            "safeArrayGet()": {
                setup: function () {
                    loadPackage("purple-secure-systems:coa-f30bc9fa-c5ce-4e8a-800f-4411cbce2f30");
                },
                "not found returns null": function () {
                    assert.isNull(classUnderTest.safeArrayGet(simpleObject, "bad.property.name", passthrough, this));
                },
                "not an array returns null": function () {
                    assert.isNull(classUnderTest.safeArrayGet(simpleObject, "prop1", passthrough, this));
                },
                "simple property path returns value": function () {
                    assert.deepEqual(classUnderTest.safeArrayGet(simpleObject, "prop2", passthrough, this), ["One", "Two"]);
                },
                "compound property path returns value": function () {
                    assert.deepEqual(classUnderTest.safeArrayGet(simpleObject, "sub1.sub1prop1", passthrough, this), ["Alpha", "Beta"]);
                }
            },
            "safeListGet()": {
                setup: function () {
                    loadPackage("purple-secure-systems:coa-f30bc9fa-c5ce-4e8a-800f-4411cbce2f30");
                },
                "not found returns empty string": function () {
                    assert.equal(classUnderTest.safeListGet(simpleObject, "bad.property.name", "value.key"), "");
                },
                "not an array returns empty string": function () {
                    assert.equal(classUnderTest.safeListGet(simpleObject, "prop1", "value.key"), "");
                },
                "simple property path returns value": function () {
                    assert.equal(classUnderTest.safeListGet(simpleObject, "sub2", "value"), "Hello, World");
                },
                "compound property path returns value": function () {
                    assert.equal(classUnderTest.safeListGet(simpleObject, "sub1.sub1prop2", "value"), "One, Two");
                },
                "compound property path returns value - custom separator": function () {
                    assert.equal(classUnderTest.safeListGet(simpleObject, "sub2", "name", ".."), "alpha..beta");
                }
            },
            "safeReferenceArrayGet()": {
                setup: function () {
                    loadPackage("purple-secure-systems:coa-f30bc9fa-c5ce-4e8a-800f-4411cbce2f30");
                },
                "not found returns null": function () {
                    assert.isNull(classUnderTest.safeReferenceArrayGet(classUnderTest.root, "abc", "123"));
                },
                "found returns array of STIX objects": function () {
                    var actual = classUnderTest.safeReferenceArrayGet(classUnderTest._data.courses_of_action[0], "related_coas.coas", "course_of_action.idref");
                    assert.isArray(actual);
                    assert.lengthOf(actual, 1);
                    assert.equal(actual[0].id(), "purple-secure-systems:coa-c26fd863-4438-4ba0-b433-9d532bd01064");
                }
            }
        }
    });
});

