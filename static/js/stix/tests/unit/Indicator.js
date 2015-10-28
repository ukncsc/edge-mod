define([
    "intern!object",
    "intern/chai!assert",
    "stix/StixPackage",
    "stix/CourseOfAction",
    "stix/Indicator",
    "stix/Observable",
    "stix/TTP",
    "intern/dojo/text!./data/Indicator_package_01.json",
    "intern/dojo/text!./data/Indicator_package_02.json",
    "intern/dojo/text!./data/Indicator_package_03.json"
], function (registerSuite, assert, StixPackage, CourseOfAction, Indicator, Observable, TTP, package01, package02, package03) {
    "use strict";

    // statics go here
    var packageData = Object.freeze({
        "purple-secure-systems:indicator-a29bda62-395a-4ac4-bfe2-761228ff3619": Object.freeze(JSON.parse(package01)),
        "fireeye:indicator-35dc3aed-d934-41c8-b920-5a5c9e814d41": Object.freeze(JSON.parse(package02)),
        "fireeye:indicator-d06e4685-15a9-43b1-b356-e6440b05ed6d": Object.freeze(JSON.parse(package03))
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
                "has correct Handling Caveats": function () {
                    assert.equal(classUnderTest.handlingCaveats(), "Unclassified, Public");
                },
                "has correct Terms of Use": function () {
                    assert.equal(classUnderTest.termsOfUse(), "Public Domain");
                },
                "has correct producer": function () {
                    assert.equal(classUnderTest.producer(), "Purple Secure Systems");
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
                "has correct indicated TTPs" : function () {
                    var actual = classUnderTest.indicatedTTPs();
                    assert.isArray(actual);
                    assert.lengthOf(actual, 1);
                    var actualIndicatedTTP = actual[0];
                    assert.instanceOf(actualIndicatedTTP, TTP);
                    assert.equal(actualIndicatedTTP.id(), "purple-secure-systems:ttp-fd4a07b1-0649-4d95-a5f2-761deb09ba32");
                },
                "has correct suggested COAs": function () {
                    var actual = classUnderTest.suggestedCOAs();
                    assert.isArray(actual);
                    assert.lengthOf(actual, 1);
                    var actualSuggestedCOA = actual[0];
                    assert.instanceOf(actualSuggestedCOA, CourseOfAction);
                    assert.equal(actualSuggestedCOA.id(), "purple-secure-systems:coa-c26fd863-4438-4ba0-b433-9d532bd01064");
                }
            },
            "valid composite indicators": {
                setup: function () {
                    loadPackage("fireeye:indicator-35dc3aed-d934-41c8-b920-5a5c9e814d41");
                },
                "has correct composite indicator expression": function () {
                    var actual = classUnderTest.compositeIndicatorComposition();
                    assert.equal(actual, "OR");
                },
                "has correct composite indicators": function () {
                    var actual = classUnderTest.compositeIndicators();
                    assert.deepEqual(actual.map(function(item) {
                        return item.id();
                    }), [
                        "fireeye:indicator-d06e4685-15a9-43b1-b356-e6440b05ed6d",
                        "fireeye:indicator-56dc9707-3656-4ebf-a6d3-6b979aca2ad6",
                        "fireeye:indicator-f2c4c357-0c73-4d4b-86b2-a8a787afe5a1",
                        "fireeye:indicator-9bf1be84-cf12-4b62-8baa-755c7a5438e8",
                        "fireeye:indicator-ac185665-2fc9-443b-94b9-fedb9e1d5494",
                        "fireeye:indicator-cd5515a5-cc36-4541-9579-78f810c45c8d",
                        "fireeye:indicator-4fd76fab-a2c1-4025-8e2c-0ff97ca3d376",
                        "fireeye:indicator-f7663237-55da-4d1c-aa52-6b24d39c47f7",
                        "fireeye:indicator-e9c5f7c7-dee3-44e7-b2ee-c105aa08e634"
                    ]);
                }
            },
            "valid non-composition observables": {
                setup: function () {
                    loadPackage("fireeye:indicator-d06e4685-15a9-43b1-b356-e6440b05ed6d");
                },
                "has correct observable": function () {
                    var actual = classUnderTest.observable();
                    assert.instanceOf(actual, Observable);
                    assert.equal(actual.id(), "fireeye:observable-f8ecdc30-c052-4efb-9aa1-3a26a7a32928");
                }
            }
        }
    });
});

