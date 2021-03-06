define([
    "intern!object",
    "intern/chai!assert",
    "stix/ReviewValue",
    "stix/StixPackage",
    "stix/ValidationInfo",
    "intern/dojo/text!./data/COA_package_01.json",
    "intern/dojo/text!./data/TTP_package_01.json",
    "stix/tests/unit/CreateEdges"
], function (registerSuite, assert, ReviewValue, StixPackage, ValidationInfo, package01, package02, CreateEdges) {
    "use strict";

    // statics go here
    var packageData = Object.freeze({
        "purple-secure-systems:coa-00000000-0000-0000-0000-000000000000": Object.freeze({}),
        "purple-secure-systems:coa-f30bc9fa-c5ce-4e8a-800f-4411cbce2f30": Object.freeze(JSON.parse(package01)),
        "purple-secure-systems:ttp-6f879a43-2e10-41d6-ba7a-b3ba8844ca59": Object.freeze(JSON.parse(package02))
    });
    var simpleObject = Object.freeze({
        prop1: "value1",
        prop2: [],
        prop3: [
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

        function loadPackage(/*String*/ packageId, /*String?*/ rootId, /*Object?*/ validationInfo) {
            classUnderTest = new StixPackage(packageData[packageId], rootId || packageId, [], validationInfo,
                CreateEdges.createEdges([
                    "purple-secure-systems:coa-f30bc9fa-c5ce-4e8a-800f-4411cbce2f30",
                    "purple-secure-systems:coa-c26fd863-4438-4ba0-b433-9d532bd01064",
                    "purple-secure-systems:ttp-6f879a43-2e10-41d6-ba7a-b3ba8844ca59"
                ]));
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
            "valid package": {
                setup: function () {
                    loadPackage("purple-secure-systems:coa-f30bc9fa-c5ce-4e8a-800f-4411cbce2f30");
                },
                "returns non-null": function () {
                    assert.isNotNull(classUnderTest.root);
                },
                "has correct id": function () {
                    assert.equal(classUnderTest.root.id, "purple-secure-systems:coa-f30bc9fa-c5ce-4e8a-800f-4411cbce2f30");
                }
            },
            "findByid": {
                setup: function () {
                    loadPackage("purple-secure-systems:coa-f30bc9fa-c5ce-4e8a-800f-4411cbce2f30");
                },
                "not a StixId": function () {
                    assert.throws(
                        function () {
                            classUnderTest.findById("purple-secure-systems:coa-c26fd863-4438-4ba0-b433-9d532bd01064");
                        },
                        "Identifier must be a StixId: purple-secure-systems:coa-c26fd863-4438-4ba0-b433-9d532bd01064"
                    );
                }
            },
            "findByStringid": {
                setup: function () {
                    loadPackage("purple-secure-systems:coa-f30bc9fa-c5ce-4e8a-800f-4411cbce2f30");
                },
                "found": function () {
                    var actual = classUnderTest.findByStringId("purple-secure-systems:coa-c26fd863-4438-4ba0-b433-9d532bd01064");
                    assert.equal(actual.id, "purple-secure-systems:coa-c26fd863-4438-4ba0-b433-9d532bd01064")
                },
                "found from cache": function () {
                    var actual = classUnderTest.findByStringId("purple-secure-systems:coa-c26fd863-4438-4ba0-b433-9d532bd01064");
                    assert.equal(actual.id, "purple-secure-systems:coa-c26fd863-4438-4ba0-b433-9d532bd01064")
                }
            },
            "header() no header": {
                setup: function () {
                    loadPackage("purple-secure-systems:ttp-6f879a43-2e10-41d6-ba7a-b3ba8844ca59");
                },
                "empty structure returned": function () {
                    assert.deepEqual(classUnderTest.header(), {});
                }
            },
            "header() has header": {
                setup: function () {
                    loadPackage("purple-secure-systems:coa-f30bc9fa-c5ce-4e8a-800f-4411cbce2f30");
                },
                "header structure returned": function () {
                    assert.deepEqual(classUnderTest.header(), {
                        handling: [
                            {
                                controlled_structure: "../../../../descendant-or-self::node()",
                                marking_structures: [
                                    {
                                        color: "WHITE",
                                        "xsi:type": "tlpMarking:TLPMarkingStructureType"
                                    }
                                ]
                            }
                        ]
                    });
                }
            },
            "validations() no validations": {
                setup: function () {
                    loadPackage("purple-secure-systems:ttp-6f879a43-2e10-41d6-ba7a-b3ba8844ca59");
                },
                "ValidationInfo returned": function () {
                    assert.instanceOf(classUnderTest.validations(), ValidationInfo);
                }
            },
            "validations() has validations": {
                setup: function () {
                    loadPackage("purple-secure-systems:ttp-6f879a43-2e10-41d6-ba7a-b3ba8844ca59", null, {});
                },
                "ValidationInfo returned": function () {
                    assert.instanceOf(classUnderTest.validations(), ValidationInfo);
                }
            },
            "safeGet()": {
                //setup: function () {
                //    loadPackage("purple-secure-systems:coa-f30bc9fa-c5ce-4e8a-800f-4411cbce2f30");
                //},
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
            "safeValueGet()": {
                setup: function () {
                    loadPackage("purple-secure-systems:coa-f30bc9fa-c5ce-4e8a-800f-4411cbce2f30");
                },
                "not found returns null": function () {
                    var actual = classUnderTest.safeValueGet("", simpleObject, "bad.property.name");
                    assert.instanceOf(actual, ReviewValue);
                    assert.isTrue(actual.isEmpty);
                    assert.isNull(actual.value);
                },
                "simple property path returns value": function () {
                    var actual = classUnderTest.safeValueGet("", simpleObject, "prop1");
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    assert.equal(actual.value, "value1");
                },
                "compound property path returns value": function () {
                    var actual = classUnderTest.safeValueGet("", simpleObject, "sub1.sub1sub.sub1subprop1");
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    assert.equal(actual.value, "sub1subvalue1");
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
                "empty array returns null": function () {
                    assert.isNull(classUnderTest.safeArrayGet(simpleObject, "prop2", passthrough, this));
                },
                "simple property path returns value": function () {
                    assert.deepEqual(classUnderTest.safeArrayGet(simpleObject, "prop3", passthrough, this), ["One", "Two"]);
                },
                "compound property path returns value": function () {
                    assert.deepEqual(classUnderTest.safeArrayGet(simpleObject, "sub1.sub1prop1", passthrough, this), ["Alpha", "Beta"]);
                },
                "compound property path returns value (no callback binding)": function () {
                    assert.deepEqual(classUnderTest.safeArrayGet(simpleObject, "sub1.sub1prop1", passthrough), ["Alpha", "Beta"]);
                }
            },
            "safeListGet()": {
                setup: function () {
                    loadPackage("purple-secure-systems:coa-f30bc9fa-c5ce-4e8a-800f-4411cbce2f30");
                },
                "not found returns empty ReviewValue": function () {
                    var actual = classUnderTest.safeListGet("", simpleObject, "bad.property.name", "value.key");
                    assert.instanceOf(actual, ReviewValue);
                    assert.isTrue(actual.isEmpty);
                },
                "not an array returns empty ReviewValue": function () {
                    var actual = classUnderTest.safeListGet("", simpleObject, "prop1", "value.key");
                    assert.instanceOf(actual, ReviewValue);
                    assert.isTrue(actual.isEmpty);
                },
                "simple property path returns value": function () {
                    var actual = classUnderTest.safeListGet("", simpleObject, "sub2", "value");
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    assert.equal(actual.value, "Hello, World");
                },
                "compound property path returns value": function () {
                    var actual = classUnderTest.safeListGet("", simpleObject, "sub1.sub1prop2", "value");
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    assert.equal(actual.value, "One, Two");
                },
                "compound property path returns value - custom separator": function () {
                    var actual = classUnderTest.safeListGet("", simpleObject, "sub2", "name", null, "..");
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    assert.equal(actual.value, "alpha..beta");
                }
            },
            "safeReferenceArrayGet()": {
                setup: function () {
                    loadPackage("purple-secure-systems:coa-f30bc9fa-c5ce-4e8a-800f-4411cbce2f30");
                },
                "not found returns null": function () {
                    var actual = classUnderTest.safeReferenceArrayGet("", classUnderTest.root, "abc", "123");
                    assert.instanceOf(actual, ReviewValue);
                    assert.isTrue(actual.isEmpty);
                    assert.isNull(actual.value);
                },
                "found returns array of STIX objects": function () {
                    var actual = classUnderTest.safeReferenceArrayGet("", classUnderTest._data.courses_of_action[0], "related_coas.coas", "course_of_action.idref");
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    var actualSTIXObjects = actual.value;
                    assert.isArray(actualSTIXObjects);
                    assert.lengthOf(actualSTIXObjects, 1);
                    assert.equal(actualSTIXObjects[0].id, "purple-secure-systems:coa-c26fd863-4438-4ba0-b433-9d532bd01064");
                }
            },
            "retrieveIdentity()": {
                setup: function () {
                    loadPackage("purple-secure-systems:coa-f30bc9fa-c5ce-4e8a-800f-4411cbce2f30");
                },
                "not found returns stubbed missing value": function () {
                    var actual = classUnderTest.retrieveIdentity(classUnderTest._data, "reporter.identity.name");
                    assert.equal(actual, "(Missing)");
                }
            },
            "retrieveIdentity() with existing identities": {
                setup: function () {
                    loadPackage("purple-secure-systems:ttp-6f879a43-2e10-41d6-ba7a-b3ba8844ca59");
                },
                "returns identity name": function () {
                    var actual = classUnderTest.retrieveIdentity(classUnderTest._data.ttps.ttps[0], "victim_targeting.identity.name");
                    assert.equal(actual._latestValue, "Primary Target");
                }
            }
        }
    });
});

