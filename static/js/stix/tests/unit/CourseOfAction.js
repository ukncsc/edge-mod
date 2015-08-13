define([
    "intern!object",
    "intern/chai!assert",
    "stix/StixPackage",
    "stix/CourseOfAction",
    "intern/dojo/text!./data/COA_package_01.json"
], function (registerSuite, assert, StixPackage, CourseOfAction, package01) {
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
                    assert.equal(classUnderTest.title(), "Suspension");
                },
                "has correct short description": function () {
                    assert.equal(classUnderTest.shortDescription(), "Suspend the employee");
                },
                "has correct description": function () {
                    assert.equal(classUnderTest.description(), "Suspend the employee for up to 48 hours while a full investigation is carried out");
                },
                "has correct TLP": function () {
                    assert.equal(classUnderTest.tlp(), "AMBER");
                },
                "has correct stage": function () {
                    assert.equal(classUnderTest.stage(), "Response");
                },
                "has correct type": function () {
                    assert.equal(classUnderTest.type(), "Policy Actions");
                },
                "has correct objective": function () {
                    assert.equal(classUnderTest.objective(), "Prevent hiding of evidence by perpetrator");
                },
                "has correct impact": function () {
                    assert.equal(classUnderTest.impact(), "Loss of productivity");
                },
                "has correct efficacy": function () {
                    assert.equal(classUnderTest.efficacy(), "No access to affected systems");
                },
                "has correct cost": function () {
                    assert.equal(classUnderTest.cost(), "Up to 2 days pay");
                },
                "has correct properties": function () {
                    assert.deepEqual(classUnderTest.properties(), [
                        {label: "stage", value: "Response"},
                        {label: "type", value: "Policy Actions"},
                        {label: "objective", value: "Prevent hiding of evidence by perpetrator"},
                        {label: "impact", value: "Loss of productivity"},
                        {label: "efficacy", value: "No access to affected systems"},
                        {label: "cost", value: "Up to 2 days pay"}
                    ]);
                },
                "has correct related COAs": function () {
                    var actual = classUnderTest.relatedCOAs();
                    assert.isArray(actual);
                    assert.lengthOf(actual, 1);
                    var actualRelatedCOA = actual[0];
                    assert.instanceOf(actualRelatedCOA, CourseOfAction);
                    assert.equal(actualRelatedCOA.id(), "purple-secure-systems:coa-c26fd863-4438-4ba0-b433-9d532bd01064");
                }
            }
        }
    });
});

