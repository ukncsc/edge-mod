define([
    "intern!object",
    "intern/chai!assert",
    "stix/StixPackage",
    "stix/CourseOfAction",
    "stix/Indicator",
    "stix/Observable",
    "intern/dojo/text!./data/Indicator_package_01.json"
], function (registerSuite, assert, StixPackage, CourseOfAction, Indicator, Observable, package01) {
    "use strict";

    // statics go here
    var packageData = Object.freeze({
        "purple-secure-systems:indicator-a29bda62-395a-4ac4-bfe2-761228ff3619": Object.freeze(JSON.parse(package01))
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
            name: "stix/Indicator",
            "valid package": {
                setup: function () {
                    loadPackage("purple-secure-systems:indicator-a29bda62-395a-4ac4-bfe2-761228ff3619");
                },
                "returns non-null": function () {
                    assert.isNotNull(classUnderTest);
                },
                "has correct id": function () {
                    assert.equal(classUnderTest.id(), "purple-secure-systems:indicator-a29bda62-395a-4ac4-bfe2-761228ff3619");
                },
                "has correct title": function () {
                    assert.equal(classUnderTest.title(), "Fully populated indicator");
                },
                "has correct short description": function () {
                    assert.equal(classUnderTest.shortDescription(), "Every field has a value");
                },
                "has correct description": function () {
                    assert.equal(classUnderTest.description(), "Every field, collection, etc has a value");
                },
                "has correct TLP": function () {
                    assert.equal(classUnderTest.tlp(), "RED");
                },
                "has correct producer": function () {
                    // TODO: add producer data to ./data/indicator_package_01.json
                    //assert.equal(classUnderTest.producer(), "Producer");
                },
                "has correct confidence": function () {
                    assert.equal(classUnderTest.confidence(), "High");
                },
                "has correct indicator types": function () {
                    assert.equal(classUnderTest.indicatorTypes(), "Malware Artifacts");
                },
                "has correct observable": function () {
                    var actual = classUnderTest.observable();
                    assert.instanceOf(actual, Observable);
                    assert.equal(actual.id(), "purple-secure-systems:observable-346b24fb-52a3-40b3-9e1c-c30985a1253a");
                },
                "has correct composition": function () {
                    assert.equal(classUnderTest.composition(), "AND");
                },
                "has correct observables": function () {
                    var actual = classUnderTest.observables();
                    assert.isArray(actual);
                    assert.lengthOf(actual, 3);
                    var actualRelatedIndicator1 = actual[0];
                    assert.instanceOf(actualRelatedIndicator1, Observable);
                    assert.equal(actualRelatedIndicator1.id(), "purple-secure-systems:observable-4a7c90a4-7735-440b-a6d9-d81ee0632449");
                    var actualRelatedIndicator2 = actual[1];
                    assert.instanceOf(actualRelatedIndicator2, Observable);
                    assert.equal(actualRelatedIndicator2.id(), "purple-secure-systems:Observable-9e96c799-7710-425f-a308-d4b6716f930c");
                    var actualRelatedIndicator3 = actual[2];
                    assert.instanceOf(actualRelatedIndicator3, Observable);
                    assert.equal(actualRelatedIndicator3.id(), "purple-secure-systems:Observable-043c5263-c43a-4e7a-adff-553a04e4cc34");
                },
                "has correct related indicators": function () {
                    var actual = classUnderTest.relatedIndicators();
                    assert.isArray(actual);
                    assert.lengthOf(actual, 1);
                    var actualRelatedIndicator = actual[0];
                    assert.instanceOf(actualRelatedIndicator, Indicator);
                    assert.equal(actualRelatedIndicator.id(), "purple-secure-systems:Indicator-7fc78054-e6f4-4b13-b3fc-44b1f4e2d9b8");
                },
                "has correct suggested COAs": function () {
                    var actual = classUnderTest.suggestedCOAs();
                    assert.isArray(actual);
                    assert.lengthOf(actual, 1);
                    var actualSuggestedCOA = actual[0];
                    assert.instanceOf(actualSuggestedCOA, CourseOfAction);
                    assert.equal(actualSuggestedCOA.id(), "purple-secure-systems:coa-c26fd863-4438-4ba0-b433-9d532bd01064");
                }
            }
        }
    });
});

