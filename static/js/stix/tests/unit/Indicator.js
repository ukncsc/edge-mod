if (typeof window === "undefined") {
    window = {};
}
window["killChainPhases"] = {
    "stix:TTP-79a0e041-9d5f-49bb-ada4-8322622b162d": "Delivery",
    "stix:TTP-af1016d6-a744-4ed7-ac91-00fe2272185a": "Reconnaissance",
    "stix:TTP-786ca8f9-2d9a-4213-b38e-399af4a2e5d6": "Actions on Objectives",
    "stix:TTP-445b4827-3cca-42bd-8421-f2e947133c16": "Weaponization",
    "stix:TTP-d6dc32b9-2538-4951-8733-3cb9ef1daae2": "Command and Control",
    "stix:TTP-f706e4e7-53d8-44ef-967f-81535c9db7d0": "Exploitation",
    "stix:TTP-e1e4e3f7-be3b-4b39-b80a-a593cfd99a4f": "Installation"
};
define([
    "intern!object",
    "intern/chai!assert",
    "stix/ReviewValue",
    "stix/StixPackage",
    "stix/CourseOfAction",
    "stix/Indicator",
    "stix/Observable",
    "stix/TTP",
    "intern/dojo/text!./data/Indicator_package_01.json",
    "intern/dojo/text!./data/Indicator_package_02.json",
    "intern/dojo/text!./data/Indicator_package_03.json",
    "intern/dojo/text!./data/Indicator_package_04.json",
    "stix/tests/unit/CreateEdges"
], function (registerSuite, assert, ReviewValue, StixPackage, CourseOfAction, Indicator, Observable, TTP, package01, package02, package03, package04, CreateEdges) {
    "use strict";

    // statics go here
    var packageData = Object.freeze({
        "purple-secure-systems:indicator-a29bda62-395a-4ac4-bfe2-761228ff3619": Object.freeze(JSON.parse(package01)),
        "fireeye:indicator-35dc3aed-d934-41c8-b920-5a5c9e814d41": Object.freeze(JSON.parse(package02)),
        "fireeye:indicator-d06e4685-15a9-43b1-b356-e6440b05ed6d": Object.freeze(JSON.parse(package03)),
        "purple-secure-systems:indicator-a29bda62-395a-4ac4-bfe2-761228ff3629": Object.freeze(JSON.parse(package04)),
    });

    return registerSuite(function () {

        // suite variables go here
        var stixPackage = null;
        var classUnderTest = null;

        function loadPackage(rootId) {
            stixPackage = new StixPackage(packageData[rootId], rootId, [], {},
                CreateEdges.createEdges([
                    "purple-secure-systems:indicator-a29bda62-395a-4ac4-bfe2-761228ff3619",
                    "purple-secure-systems:indicator-1cf691e8-6428-402c-a28e-b609ba7d6d2d",
                    "fireeye:indicator-35dc3aed-d934-41c8-b920-5a5c9e814d41",
                    "fireeye:indicator-d06e4685-15a9-43b1-b356-e6440b05ed6d",
                    "purple-secure-systems:indicator-a29bda62-395a-4ac4-bfe2-761228ff3629",
                    "purple-secure-systems:observable-346b24fb-52a3-40b3-9e1c-c30985a1253a",
                    "purple-secure-systems:observable-4a7c90a4-7735-440b-a6d9-d81ee0632449",
                    "purple-secure-systems:Observable-9e96c799-7710-425f-a308-d4b6716f930c",
                    "purple-secure-systems:Observable-043c5263-c43a-4e7a-adff-553a04e4cc34",
                    "purple-secure-systems:Indicator-7fc78054-e6f4-4b13-b3fc-44b1f4e2d9b8",
                    "purple-secure-systems:ttp-fd4a07b1-0649-4d95-a5f2-761deb09ba32",
                    "purple-secure-systems:coa-c26fd863-4438-4ba0-b433-9d532bd01064",
                    "fireeye:indicator-35dc3aed-d934-41c8-b920-5a5c9e814d41",
                    "fireeye:indicator-d06e4685-15a9-43b1-b356-e6440b05ed6d",
                    "fireeye:indicator-56dc9707-3656-4ebf-a6d3-6b979aca2ad6",
                    "fireeye:indicator-f2c4c357-0c73-4d4b-86b2-a8a787afe5a1",
                    "fireeye:indicator-9bf1be84-cf12-4b62-8baa-755c7a5438e8",
                    "fireeye:indicator-ac185665-2fc9-443b-94b9-fedb9e1d5494",
                    "fireeye:indicator-cd5515a5-cc36-4541-9579-78f810c45c8d",
                    "fireeye:indicator-4fd76fab-a2c1-4025-8e2c-0ff97ca3d376",
                    "fireeye:indicator-f7663237-55da-4d1c-aa52-6b24d39c47f7",
                    "fireeye:indicator-e9c5f7c7-dee3-44e7-b2ee-c105aa08e634",
                    "fireeye:observable-f8ecdc30-c052-4efb-9aa1-3a26a7a32928",
                    "pss:TTP-f5ddf190-b7b0-4c33-a9f4-f2beb6453d04",
                    "purple-secure-systems:indicator-a29bda62-395a-4ac4-bfe2-761228ff3629"
                ]));
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
                    var actual = classUnderTest.title();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty());
                    assert.equal(actual.value(), "Fully populated indicator");
                },
                "has correct short description": function () {
                    var actual = classUnderTest.shortDescription();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty());
                    assert.equal(actual.value(), "Every field has a value");
                },
                "has correct description": function () {
                    var actual = classUnderTest.description();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty());
                    assert.equal(actual.value(), "Every field, collection, etc has a value");
                },
                "has correct TLP": function () {
                    var actual = classUnderTest.tlp();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty());
                    assert.equal(actual.value(), "RED");
                },
                "has correct Marking": function () {
                    var actual = classUnderTest.marking();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty());
                    assert.equal(actual.value(), "Unclassified, Public");
                },
                "has correct Terms of Use": function () {
                    var actual = classUnderTest.termsOfUse();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty());
                    assert.equal(actual.value(), "Public Domain");
                },
                "has correct producer": function () {
                    var actual = classUnderTest.producer();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty());
                    assert.equal(actual.value(), "Purple Secure Systems");
                },
                "has correct confidence": function () {
                    var actual = classUnderTest.confidence();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty());
                    assert.equal(actual.value(), "High");
                },
                "has correct indicator types": function () {
                    var actual = classUnderTest.indicatorTypes();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty());
                    assert.equal(actual.value(), "Malware Artifacts");
                },
                "has correct kill chain phase": function () {
                    var actual = classUnderTest.killChainPhase();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty());
                    assert.equal(actual.value(), "Reconnaissance");
                },
                "has correct observable": function () {
                    var actual = classUnderTest.observable();
                    assert.instanceOf(actual, Observable);
                    assert.equal(actual.id(), "purple-secure-systems:observable-346b24fb-52a3-40b3-9e1c-c30985a1253a");
                },
                "has correct composition": function () {
                    var actual = classUnderTest.composition();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty());
                    assert.equal(actual.value(), "AND");
                },
                "has correct observables": function () {
                    var actual = classUnderTest.observables();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty());
                    var actualObservables = actual.value();
                    assert.isArray(actualObservables);
                    assert.lengthOf(actualObservables, 3);
                    var actualObservable1 = actualObservables[0];
                    assert.instanceOf(actualObservable1, Observable);
                    assert.equal(actualObservable1.id(), "purple-secure-systems:observable-4a7c90a4-7735-440b-a6d9-d81ee0632449");
                    var actualObservable2 = actualObservables[1];
                    assert.instanceOf(actualObservable2, Observable);
                    assert.equal(actualObservable2.id(), "purple-secure-systems:Observable-9e96c799-7710-425f-a308-d4b6716f930c");
                    var actualObservable3 = actualObservables[2];
                    assert.instanceOf(actualObservable3, Observable);
                    assert.equal(actualObservable3.id(), "purple-secure-systems:Observable-043c5263-c43a-4e7a-adff-553a04e4cc34");
                },
                "has correct related indicators": function () {
                    var actual = classUnderTest.relatedIndicators();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty());
                    var actualRelatedIndicators = actual.value();
                    assert.isArray(actualRelatedIndicators);
                    assert.lengthOf(actualRelatedIndicators, 1);
                    var actualRelatedIndicator = actualRelatedIndicators[0];
                    assert.instanceOf(actualRelatedIndicator, Indicator);
                    assert.equal(actualRelatedIndicator.id(), "purple-secure-systems:Indicator-7fc78054-e6f4-4b13-b3fc-44b1f4e2d9b8");
                },
                "has correct indicated TTPs": function () {
                    var actual = classUnderTest.indicatedTTPs();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty());
                    var actualIndicatedTTPs = actual.value();
                    assert.isArray(actualIndicatedTTPs);
                    assert.lengthOf(actualIndicatedTTPs, 1);
                    var actualIndicatedTTP = actualIndicatedTTPs[0];
                    assert.instanceOf(actualIndicatedTTP, TTP);
                    assert.equal(actualIndicatedTTP.id(), "purple-secure-systems:ttp-fd4a07b1-0649-4d95-a5f2-761deb09ba32");
                },
                "has correct suggested COAs": function () {
                    var actual = classUnderTest.suggestedCOAs();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty());
                    var actualSuggestedCOAs = actual.value();
                    assert.isArray(actualSuggestedCOAs);
                    assert.lengthOf(actualSuggestedCOAs, 1);
                    var actualSuggestedCOA = actualSuggestedCOAs[0];
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
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty());
                    assert.equal(actual.value(), "OR");
                },
                "has correct composite indicators": function () {
                    var actual = classUnderTest.compositeIndicators();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty());
                    var actualCompositeIndicators = actual.value();
                    assert.deepEqual(actualCompositeIndicators.map(function (item) {
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
            "valid non-composition observable": {
                setup: function () {
                    loadPackage("fireeye:indicator-d06e4685-15a9-43b1-b356-e6440b05ed6d");
                },
                "has correct observable": function () {
                    var actual = classUnderTest.observable();
                    assert.instanceOf(actual, Observable);
                    assert.equal(actual.id(), "fireeye:observable-f8ecdc30-c052-4efb-9aa1-3a26a7a32928");
                },
                "has correct observables": function () {
                    var actual = classUnderTest.observables();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty());
                    var actualObservables = actual.value();
                    assert.isArray(actualObservables);
                    assert.lengthOf(actualObservables, 1);
                    var actualObservable = actualObservables[0];
                    assert.instanceOf(actualObservable, Observable);
                    assert.equal(actualObservable.id(), "fireeye:observable-f8ecdc30-c052-4efb-9aa1-3a26a7a32928");
                },
                "has correct kill chain phase": function () {
                    var actual = classUnderTest.killChainPhase();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty());
                    assert.equal(actual.value(), "pss:TTP-f5ddf190-b7b0-4c33-a9f4-f2beb6453d04");
                }
            },
            "no observable indicator": {
                setup: function () {
                    loadPackage("purple-secure-systems:indicator-a29bda62-395a-4ac4-bfe2-761228ff3629");
                },
                "has correct observables": function () {
                    var actual = classUnderTest.observables();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isTrue(actual.isEmpty());
                },
            }
        }
    });
});

