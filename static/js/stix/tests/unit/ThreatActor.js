define([
    "intern!object",
    "intern/chai!assert",
    "stix/ReviewValue",
    "stix/StixPackage",
    "stix/ThreatActor",
    "stix/TTP",
    "stix/Campaign",
    "intern/dojo/text!./data/ThreatActor_package_01.json",
    "stix/tests/unit/CreateEdges"
], function (registerSuite, assert, ReviewValue, StixPackage, ThreatActor, TTP, Campaign, package01, CreateEdges) {
    "use strict";

    // statics go here
    var packageData = Object.freeze({
        "pss:threatactor-0bdab62c-3a6b-46ff-b3ce-59507b1aa4ed": Object.freeze(JSON.parse(package01))
    });

    return registerSuite(function () {

        // suite variables go here
        var stixPackage = null;
        var classUnderTest = null;

        function loadPackage(rootId) {
            stixPackage = new StixPackage(packageData[rootId], rootId, [], {},
                CreateEdges.createEdges([
                    "pss:threatactor-0bdab62c-3a6b-46ff-b3ce-59507b1aa4ed",
                    "opensource:ttp-70fe9862-02f1-4561-9892-209023f2b42c",
                    "pss:threatactor-377173e0-08c4-4ce4-aa7d-347cdbc69775",
                    "pss:campaign-658d8c83-b38b-4979-8ec9-125653e680c7"
                ]));
            classUnderTest = stixPackage.root;
        }

        return {
            name: "stix/ThreatActor",
            "valid package": {
                setup: function () {
                    loadPackage("pss:threatactor-0bdab62c-3a6b-46ff-b3ce-59507b1aa4ed");
                },
                "returns non-null": function () {
                    assert.isNotNull(classUnderTest);
                },
                "has correct id": function () {
                    assert.equal(classUnderTest.id(), "pss:threatactor-0bdab62c-3a6b-46ff-b3ce-59507b1aa4ed");
                },
                "has correct title": function () {
                    var actual = classUnderTest.title();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    assert.equal(actual.value, "Exemplar");
                },
                "has correct short description": function () {
                    var actual = classUnderTest.shortDescription();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    assert.equal(actual.value, "short description");
                },
                "has correct description": function () {
                    var actual = classUnderTest.description();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    assert.equal(actual.value, "LONG Description");
                },
                "has correct TLP": function () {
                    var actual = classUnderTest.tlp();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    assert.equal(actual.value, "AMBER");
                },
                "has correct types": function () {
                    var actual = classUnderTest.types();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    assert.equal(actual.value, "Hacktivist, Hacker");
                },
                "has correct motivations": function () {
                    var actual = classUnderTest.motivations();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    assert.equal(actual.value, "Financial or Economic");
                },
                "has correct sophistications": function () {
                    var actual = classUnderTest.sophistications();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    assert.equal(actual.value, "Expert");
                },
                "has correct Intended Effects": function () {
                    var actual = classUnderTest.intendedEffects();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    assert.equal(actual.value, "Degradation of Service");
                },
                "has correct planning and ops support": function () {
                    var actual = classUnderTest.operationalSupports();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    assert.equal(actual.value, "Data Exploitation");
                },
                "has correct observed TTPs": function () {
                    var actual = classUnderTest.observedTTPs();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    var actualObservedTTPs = actual.value;
                    assert.isArray(actualObservedTTPs);
                    assert.lengthOf(actualObservedTTPs, 1);
                    var actualObservedTTP = actualObservedTTPs[0];
                    assert.instanceOf(actualObservedTTP, TTP);
                    assert.equal(actualObservedTTP.id(), "opensource:ttp-70fe9862-02f1-4561-9892-209023f2b42c")
                },
                "has correct associated actors": function () {
                    var actual = classUnderTest.associatedActors();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    var actualAssociatedActors = actual.value;
                    assert.isArray(actualAssociatedActors);
                    assert.lengthOf(actualAssociatedActors, 1);
                    var actualAssociatedActor = actualAssociatedActors[0];
                    assert.instanceOf(actualAssociatedActor, ThreatActor);
                    assert.equal(actualAssociatedActor.id(), "pss:threatactor-377173e0-08c4-4ce4-aa7d-347cdbc69775")
                },
                "has correct associated campaigns": function () {
                    var actual = classUnderTest.associatedCampaigns();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    var actualAssociatedCampaigns = actual.value;
                    assert.isArray(actualAssociatedCampaigns);
                    assert.lengthOf(actualAssociatedCampaigns, 1);
                    var actualAssociatedCampaign = actualAssociatedCampaigns[0];
                    assert.instanceOf(actualAssociatedCampaign, Campaign);
                    assert.equal(actualAssociatedCampaign.id(), "pss:campaign-658d8c83-b38b-4979-8ec9-125653e680c7");
                }
            }
        }
    });
});

