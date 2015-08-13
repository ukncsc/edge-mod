define([
    "intern!object",
    "intern/chai!assert",
    "stix/StixPackage",
    "stix/TTP",
    "intern/dojo/text!./data/TTP_package_01.json"
], function (registerSuite, assert, StixPackage, TTP, package01) {
    "use strict";

    // statics go here
    var packageData = Object.freeze({
        "purple-secure-systems:ttp-00000000-0000-0000-0000-000000000000": Object.freeze({}),
        "purple-secure-systems:ttp-6f879a43-2e10-41d6-ba7a-b3ba8844ca59": Object.freeze(JSON.parse(package01))
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
            name: "stix/TTP",
            "empty package": {
                setup: function () {
                    loadPackage("purple-secure-systems:ttp-00000000-0000-0000-0000-000000000000");
                },
                "returns null": function () {
                    assert.isNull(classUnderTest);
                }
            },
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
                    assert.equal(classUnderTest.title(), "Trying everything");
                },
                "has correct short description": function () {
                    assert.equal(classUnderTest.shortDescription(), "All the tricks in the book");
                },
                "has correct description": function () {
                    assert.equal(classUnderTest.description(), "Including the kitchen sink");
                },
                "has correct TLP": function () {
                    assert.equal(classUnderTest.tlp(), "RED");
                },
                "has correct target": function () {
                    assert.equal(classUnderTest.target(), "Primary Target");
                },
                "has correct attack patterns": function () {
                    assert.equal(classUnderTest.attackPatterns(), "Pattern 1, Pattern 2, Pattern 3");
                },
                "has correct malware instances": function () {
                    assert.equal(classUnderTest.malwareInstances(), "Automated Transfer Scripts, Adware, Dialer");
                },
                "has correct intended effects": function () {
                    assert.equal(classUnderTest.intendedEffects(), "Unauthorized Access, Brand Damage, Account Takeover, Theft, Advantage");
                },
                "has correct related TTPs": function () {
                    var actual = classUnderTest.relatedTTPs();
                    assert.isArray(actual);
                    assert.lengthOf(actual, 1);
                    var actualRelatedTTP = actual[0];
                    assert.instanceOf(actualRelatedTTP, TTP);
                    assert.equal(actualRelatedTTP.id(), "purple-secure-systems:ttp-fd4a07b1-0649-4d95-a5f2-761deb09ba32");
                }
            }
        }
    });
});

