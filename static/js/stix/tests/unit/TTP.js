define([
    "intern!object",
    "intern/chai!assert",
    "stix/ReviewValue",
    "stix/StixPackage",
    "stix/TTP",
    "intern/dojo/text!./data/TTP_package_01.json",
    "stix/tests/unit/CreateEdges"
], function (registerSuite, assert, ReviewValue, StixPackage, TTP, package01, CreateEdges) {
    "use strict";

    // statics go here
    var packageData = Object.freeze({
        "purple-secure-systems:ttp-6f879a43-2e10-41d6-ba7a-b3ba8844ca59": Object.freeze(JSON.parse(package01))
    });

    return registerSuite(function () {

        // suite variables go here
        var stixPackage = null;
        var classUnderTest = null;

        function loadPackage(rootId) {
            stixPackage = new StixPackage(packageData[rootId], rootId, [], {},
                CreateEdges.createEdges([
                    "purple-secure-systems:ttp-6f879a43-2e10-41d6-ba7a-b3ba8844ca59",
                    "purple-secure-systems:ttp-fd4a07b1-0649-4d95-a5f2-761deb09ba32"
                ]));
            classUnderTest = stixPackage.root;
        }

        return {
            name: "stix/TTP",
            "valid package": {
                setup: function () {
                    loadPackage("purple-secure-systems:ttp-6f879a43-2e10-41d6-ba7a-b3ba8844ca59");
                },
                "returns non-null": function () {
                    assert.isNotNull(classUnderTest);
                },
                "has correct id": function () {
                    assert.equal(classUnderTest.id(), "purple-secure-systems:ttp-6f879a43-2e10-41d6-ba7a-b3ba8844ca59");
                },
                "has correct title": function () {
                    var actual = classUnderTest.title();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    assert.equal(actual.value, "Trying everything");
                },
                "has correct short description": function () {
                    var actual = classUnderTest.shortDescription();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    assert.equal(actual.value, "All the tricks in the book");
                },
                "has correct description": function () {
                    var actual = classUnderTest.description();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    assert.equal(actual.value, "Including the kitchen sink");
                },
                "has correct TLP": function () {
                    var actual = classUnderTest.tlp();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    assert.equal(actual.value, "RED");
                },
                "has correct target": function () {
                    var actual = classUnderTest.target();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    assert.equal(actual.value, "Primary Target");
                },
                "has correct attack patterns, concatenating capec ids into values": function () {
                    var actual = classUnderTest.attackPatterns();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    assert.equal(actual.value, "Pattern 1(CAPEC-01), Pattern 2(CAPEC-02), Pattern 3(CAPEC-03)");
                },
                "has correct malware instances": function () {
                    var actual = classUnderTest.malwareInstances();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    assert.equal(actual.value, "Automated Transfer Scripts, Adware, Dialer");
                },
                "has correct intended effects": function () {
                    var actual = classUnderTest.intendedEffects();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    assert.equal(actual.value, "Unauthorized Access, Brand Damage, Account Takeover, Theft, Advantage");
                },
                "has correct related TTPs": function () {
                    var actual = classUnderTest.relatedTTPs();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    var actualTTPs = actual.value;
                    assert.isArray(actualTTPs);
                    assert.lengthOf(actualTTPs, 1);
                    var actualRelatedTTP = actualTTPs[0];
                    assert.instanceOf(actualRelatedTTP, TTP);
                    assert.equal(actualRelatedTTP.id(), "purple-secure-systems:ttp-fd4a07b1-0649-4d95-a5f2-761deb09ba32");
                }
            }
        }
    });
});

