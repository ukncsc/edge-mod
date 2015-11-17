define([
    "intern!object",
    "intern/chai!assert",
    "stix/ReviewValue",
    "stix/StixPackage",
    "stix/CourseOfAction",
    "intern/dojo/text!./data/COA_package_01.json"
], function (registerSuite, assert, ReviewValue, StixPackage, CourseOfAction, package01) {
    "use strict";

    // statics go here
    var packageData = Object.freeze({
        "purple-secure-systems:coa-f30bc9fa-c5ce-4e8a-800f-4411cbce2f30": Object.freeze(JSON.parse(package01))
    });

    return registerSuite(function () {

        // suite variables go here
        var stixPackage = null;
        var classUnderTest = null;

        function loadPackage(rootId) {
            stixPackage = new StixPackage(packageData[rootId], rootId);
            classUnderTest = stixPackage.root;
        }

        return {
            name: "stix/CourseOfAction",
            "valid package": {
                setup: function () {
                    loadPackage("purple-secure-systems:coa-f30bc9fa-c5ce-4e8a-800f-4411cbce2f30");
                },
                "returns non-null": function () {
                    assert.isNotNull(classUnderTest);
                },
                "has correct id": function () {
                    assert.equal(classUnderTest.id(), "purple-secure-systems:coa-f30bc9fa-c5ce-4e8a-800f-4411cbce2f30");
                },
                "has correct title": function () {
                    var actual = classUnderTest.title();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty());
                    assert.equal(actual.value(), "Suspension");
                },
                "has correct short description": function () {
                    var actual = classUnderTest.shortDescription();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty());
                    assert.equal(actual.value(), "Suspend the employee");
                },
                "has correct description": function () {
                    var actual = classUnderTest.description();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty());
                    assert.equal(actual.value(), "Suspend the employee for up to 48 hours while a full investigation is carried out");
                },
                "has correct TLP": function () {
                    var actual = classUnderTest.tlp();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty());
                    assert.equal(actual.value(), "AMBER");
                },
                "has correct stage": function () {
                    var actual = classUnderTest.stage();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty());
                    assert.equal(actual.value(), "Response");
                },
                "has correct type": function () {
                    var actual = classUnderTest.type();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty());
                    assert.equal(actual.value(), "Policy Actions");
                },
                "has correct objective": function () {
                    var actual = classUnderTest.objective();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty());
                    assert.equal(actual.value(), "Prevent hiding of evidence by perpetrator");
                },
                "has correct impact": function () {
                    var actual = classUnderTest.impact();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty());
                    assert.equal(actual.value(), "Loss of productivity");
                },
                "has correct efficacy": function () {
                    var actual = classUnderTest.efficacy();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty());
                    assert.equal(actual.value(), "No access to affected systems");
                },
                "has correct cost": function () {
                    var actual = classUnderTest.cost();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty());
                    assert.equal(actual.value(), "Up to 2 days pay");
                },
                "has correct properties": function () {
                    var expectedProperties = [
                        {label: "Stage", value: "Response"},
                        {label: "Type", value: "Policy Actions"},
                        {label: "Objective", value: "Prevent hiding of evidence by perpetrator"},
                        {label: "Impact", value: "Loss of productivity"},
                        {label: "Efficacy", value: "No access to affected systems"},
                        {label: "Cost", value: "Up to 2 days pay"}
                    ];
                    var actualProperties = classUnderTest.properties();
                    assert.isArray(actualProperties);
                    assert.lengthOf(actualProperties, expectedProperties.length);
                    actualProperties.forEach(function (actualProperty, idx) {
                        var expected = expectedProperties[idx];
                        assert.equal(actualProperty.label, expected.label);
                        var actual = actualProperty.value();
                        assert.instanceOf(actual, ReviewValue);
                        assert.isFalse(actual.isEmpty());
                        assert.equal(actual.value(), expected.value);
                    });
                },
                "has correct related COAs": function () {
                    var actual = classUnderTest.relatedCOAs();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty());
                    var actualRelatedCOAs = actual.value();
                    assert.isArray(actualRelatedCOAs);
                    assert.lengthOf(actualRelatedCOAs, 1);
                    var actualRelatedCOA = actualRelatedCOAs[0];
                    assert.instanceOf(actualRelatedCOA, CourseOfAction);
                    assert.equal(actualRelatedCOA.id(), "purple-secure-systems:coa-c26fd863-4438-4ba0-b433-9d532bd01064");
                }
            }
        }
    });
});

