define([
    "intern!object",
    "intern/chai!assert",
    "stix/ReviewValue",
    "stix/StixPackage",
    "stix/Campaign",
    "stix/TTP",
    "stix/Incident",
    "stix/Indicator",
    "stix/ThreatActor",
    "intern/dojo/text!./data/Campaign_package_01.json",
    "stix/tests/unit/CreateEdges"
], function (registerSuite, assert, ReviewValue, StixPackage, Campaign, TTP, Incident, Indicator, ThreatActor, package01, CreateEdges) {
    "use strict";

    // statics go here
    var packageData = Object.freeze({
        "pss:campaign-a7bc3ff3-2d60-4d11-9a91-09ea9f6feb9c": Object.freeze(JSON.parse(package01))
    });

    return registerSuite(function () {

        // suite variables go here
        var stixPackage = null;
        var classUnderTest = null;

        function loadPackage(rootId) {
            stixPackage = new StixPackage(packageData[rootId], rootId, [], {},
                CreateEdges.createEdges([
                    "pss:campaign-a7bc3ff3-2d60-4d11-9a91-09ea9f6feb9c",
                    "opensource:ttp-70fe9862-02f1-4561-9892-209023f2b42c",
                    "pss:incident-4ac9bbd1-99c4-48b0-adfb-593e3ef384cd",
                    "pss:campaign-658d8c83-b38b-4979-8ec9-125653e680c7",
                    "pss:threatactor-0bdab62c-3a6b-46ff-b3ce-59507b1aa4ed",
                    "pss:indicator-019ac66c-131e-4f7d-9ad2-a7afa5c1640a"
                ]));
            classUnderTest = stixPackage.root;
        }

        return {
            name: "stix/Campaign",
            setup: function () {
                loadPackage("pss:campaign-a7bc3ff3-2d60-4d11-9a91-09ea9f6feb9c");
            },
            "returns non-null": function () {
                assert.isNotNull(classUnderTest);
            },
            "has correct id": function () {
                assert.equal(classUnderTest.id(), "pss:campaign-a7bc3ff3-2d60-4d11-9a91-09ea9f6feb9c");
            },
            "has correct title": function () {
                var actual = classUnderTest.title();
                assert.instanceOf(actual, ReviewValue);
                assert.isFalse(actual.isEmpty);
                assert.equal(actual.value, "Test campaign");
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
                assert.equal(actual.value, "long description");
            },
            "has correct TLP": function () {
                var actual = classUnderTest.tlp();
                assert.instanceOf(actual, ReviewValue);
                assert.isFalse(actual.isEmpty);
                assert.equal(actual.value, "WHITE");
            },
            "has correct effects": function () {
                var actual = classUnderTest.intendedEffects();
                assert.instanceOf(actual, ReviewValue);
                assert.isFalse(actual.isEmpty);
                assert.equal(actual.value, "Advantage");
            },
            "has correct names": function () {
                var actual = classUnderTest.names();
                assert.instanceOf(actual, ReviewValue);
                assert.isFalse(actual.isEmpty);
                assert.equal(actual.value, "Joe Bloggs");
            },
            "has correct related TTPs": function () {
                var actual = classUnderTest.relatedTTPs();
                assert.instanceOf(actual, ReviewValue);
                assert.isFalse(actual.isEmpty);
                var actualRelatedTTPs = actual.value;
                assert.isArray(actualRelatedTTPs);
                assert.lengthOf(actualRelatedTTPs, 1);
                var actualRelatedTTP = actualRelatedTTPs[0];
                assert.instanceOf(actualRelatedTTP, TTP);
                assert.equal(actualRelatedTTP.id(), "opensource:ttp-70fe9862-02f1-4561-9892-209023f2b42c")
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
                assert.equal(actualAssociatedCampaign.id(), "pss:campaign-658d8c83-b38b-4979-8ec9-125653e680c7")
            },
            "has correct related incidents": function () {
                var actual = classUnderTest.relatedIncidents();
                assert.instanceOf(actual, ReviewValue);
                assert.isFalse(actual.isEmpty);
                var actualRelatedIncidents = actual.value;
                assert.isArray(actualRelatedIncidents);
                assert.lengthOf(actualRelatedIncidents, 1);
                var actualRelatedIncident = actualRelatedIncidents[0];
                assert.instanceOf(actualRelatedIncident, Incident);
                assert.equal(actualRelatedIncident.id(), "pss:incident-4ac9bbd1-99c4-48b0-adfb-593e3ef384cd")
            },
            "has correct related indicators": function () {
                var actual = classUnderTest.relatedIndicators();
                assert.instanceOf(actual, ReviewValue);
                assert.isFalse(actual.isEmpty);
                var actualRelatedIndicators = actual.value;
                assert.isArray(actualRelatedIndicators);
                assert.lengthOf(actualRelatedIndicators, 1);
                var actualRelatedIndicator = actualRelatedIndicators[0];
                assert.instanceOf(actualRelatedIndicator, Indicator);
                assert.equal(actualRelatedIndicator.id(), "pss:indicator-019ac66c-131e-4f7d-9ad2-a7afa5c1640a")
            },
            "has correct related actors": function () {
                var actual = classUnderTest.relatedActors();
                assert.instanceOf(actual, ReviewValue);
                assert.isFalse(actual.isEmpty);
                var actualRelatedActors = actual.value;
                assert.isArray(actualRelatedActors);
                assert.lengthOf(actualRelatedActors, 1);
                var actualRelatedActor = actualRelatedActors[0];
                assert.instanceOf(actualRelatedActor, ThreatActor);
                assert.equal(actualRelatedActor.id(), "pss:threatactor-0bdab62c-3a6b-46ff-b3ce-59507b1aa4ed")
            }
        }
    });
});
