define([
    "intern!object",
    "intern/chai!assert",
    "stix/ReviewValue",
    "stix/StixPackage",
    "stix/Incident",
    "stix/Indicator",
    "stix/Observable",
    "stix/TTP",
    "intern/dojo/text!./data/Incident_package_01.json",
    "stix/tests/unit/CreateEdges"
], function (registerSuite, assert, ReviewValue, StixPackage, Incident, Indicator, Observable, TTP, package01, CreateEdges) {
    "use strict";

    // statics go here
    var packageData = Object.freeze({
        "purple-secure-systems:incident-02468346-fdf2-4095-a905-f3731fccd58d": Object.freeze(JSON.parse(package01))
    });

    return registerSuite(function () {

        // suite variables go here
        var stixPackage = null;
        var classUnderTest = null;

        function loadPackage(rootId) {
            stixPackage = new StixPackage(packageData[rootId], rootId, [], {},
                CreateEdges.createEdges([
                    "purple-secure-systems:incident-02468346-fdf2-4095-a905-f3731fccd58d",
                    "purple-secure-systems:ttp-fd4a07b1-0649-4d95-a5f2-761deb09ba32",
                    "purple-secure-systems:incident-2ac2d36b-fa0f-49aa-87bc-bdc27a497f19",
                    "purple-secure-systems:incident-0b0090ab-bae8-4167-a538-9cc68033f9c9",
                    "purple-secure-systems:indicator-d46e13c9-7dce-4272-a593-1cd2f9212a2d",
                    "purple-secure-systems:observable-f9faeb29-9c98-434c-b07a-4647e6cdd6f2",
                    "purple-secure-systems:observable-1fb0e40b-d23d-4b81-ab78-0824e2642ebf",
                    "purple-secure-systems:observable-9db11783-3887-4f32-9f10-f18ebf2fba98",
                    "purple-secure-systems:indicator-1cf691e8-6428-402c-a28e-b609ba7d6d2d"

                ]));
            classUnderTest = stixPackage.root;
        }

        return {
            name: "stix/Incident",
            "valid package": {
                setup: function () {
                    loadPackage("purple-secure-systems:incident-02468346-fdf2-4095-a905-f3731fccd58d");
                },
                "returns non-null": function () {
                    assert.isNotNull(classUnderTest);
                },
                "has correct id": function () {
                    assert.equal(classUnderTest.id, "purple-secure-systems:incident-02468346-fdf2-4095-a905-f3731fccd58d");
                },
                "has correct title": function () {
                    var actual = classUnderTest.title();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    assert.equal(actual.value, "Bot-net found on intranet");
                },
                "has correct short description": function () {
                    var actual = classUnderTest.shortDescription();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    assert.equal(actual.value, "Bottom bot-net running");
                },
                "has correct description": function () {
                    var actual = classUnderTest.description();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    assert.equal(actual.value, "It appears that the 'Bottom' bot-net is running on our intranet");
                },
                "has correct TLP": function () {
                    var actual = classUnderTest.tlp();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    assert.equal(actual.value, "RED");
                },
                "has correct status": function () {
                    var actual = classUnderTest.status();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    assert.equal(actual.value, "Incident Reported");
                },
                "has correct reporter": function () {
                    var actual = classUnderTest.reporter();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    assert.equal(actual.value, "Cynthia James");
                },
                "has correct confidence": function () {
                    var actual = classUnderTest.confidence();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    assert.equal(actual.value, "High");
                },
                "has correct responders": function () {
                    var actual = classUnderTest.responders();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    assert.equal(actual.value, "Responser 2, Responser 1");
                },
                "has correct intended effects": function () {
                    var actual = classUnderTest.intendedEffects();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    assert.equal(actual.value, "Unauthorized Access, Traffic Diversion, ICS Control, Harassment, Fraud, Extortion, Exposure, Embarrassment, Disruption, Destruction, Denial and Deception, Degradation of Service, Competitive Advantage, Brand Damage, Account Takeover, Theft - Theft of Proprietary Information, Theft - Identity Theft, Theft - Credential Theft, Theft - Intellectual Property, Theft - Intellectual Property, Theft, Advantage - Political, Advantage - Military, Advantage - Economic, Advantage");
                },
                "has correct discovery methods": function () {
                    var actual = classUnderTest.discoveryMethods();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    assert.equal(actual.value, "Unknown, User, Security Alarm, NIDS, Log Review, IT Audit, HIPS, Fraud Detection, Financial Audit, Incident Response, Antivirus, Audit, Unrelated Party, Customer, Law Enforcement, Monitoring Service, Fraud Detection, Agent Disclosure");
                },
                "has correct impact assessment": function () {
                    var actual = classUnderTest.impactAssessment();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    assert.equal(actual.value, "User Data Loss, Unintended Access, Regulatory, Compliance or Legal Impact, Loss of Confidential / Proprietary Information or Intellectual Property, Unintended Access, Disruption of Service / Operations, Destruction, Degradation of Service, Data Breach or Compromise, Loss of Competitive Advantage - Political, Loss of Competitive Advantage - Military, Loss of Competitive Advantage - Economic, Loss of Competitive Advantage, Brand or Image Degradation");
                },
                "has correct leveraged TTPs": function () {
                    var actual = classUnderTest.leveragedTTPs();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    var actualLeveragedTTPs = actual.value;
                    assert.isArray(actualLeveragedTTPs);
                    assert.lengthOf(actualLeveragedTTPs, 1);
                    var actualLeveragedTTP = actualLeveragedTTPs[0];
                    assert.instanceOf(actualLeveragedTTP, TTP);
                    assert.equal(actualLeveragedTTP.id, "purple-secure-systems:ttp-fd4a07b1-0649-4d95-a5f2-761deb09ba32");
                },
                "has correct related incidents": function () {
                    var actual = classUnderTest.relatedIncidents();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    var actualRelatedIncidents = actual.value;
                    assert.isArray(actualRelatedIncidents);
                    assert.lengthOf(actualRelatedIncidents, 2);
                    var actualRelatedIncident1 = actualRelatedIncidents[0];
                    assert.instanceOf(actualRelatedIncident1, Incident);
                    assert.equal(actualRelatedIncident1.id, "purple-secure-systems:incident-2ac2d36b-fa0f-49aa-87bc-bdc27a497f19");
                    var actualRelatedIncident2 = actualRelatedIncidents[1];
                    assert.instanceOf(actualRelatedIncident2, Incident);
                    assert.equal(actualRelatedIncident2.id, "purple-secure-systems:incident-0b0090ab-bae8-4167-a538-9cc68033f9c9");
                },
                "has correct related indicators": function () {
                    var actual = classUnderTest.relatedIndicators();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    var actualRelatedIndicators = actual.value;
                    assert.isArray(actualRelatedIndicators);
                    assert.lengthOf(actualRelatedIndicators, 2);
                    var actualRelatedIndicator1 = actualRelatedIndicators[0];
                    assert.instanceOf(actualRelatedIndicator1, Indicator);
                    assert.equal(actualRelatedIndicator1.id, "purple-secure-systems:indicator-d46e13c9-7dce-4272-a593-1cd2f9212a2d");
                    var actualRelatedIndicator2 = actualRelatedIndicators[1];
                    assert.instanceOf(actualRelatedIndicator2, Indicator);
                    assert.equal(actualRelatedIndicator2.id, "purple-secure-systems:indicator-1cf691e8-6428-402c-a28e-b609ba7d6d2d");
                },
                "has correct related observables": function () {
                    var actual = classUnderTest.relatedObservables();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    var actualRelatedObservables = actual.value;
                    assert.isArray(actualRelatedObservables);
                    assert.lengthOf(actualRelatedObservables, 3);
                    var actualRelatedObservable1 = actualRelatedObservables[0];
                    assert.instanceOf(actualRelatedObservable1, Observable);
                    assert.equal(actualRelatedObservable1.id, "purple-secure-systems:observable-f9faeb29-9c98-434c-b07a-4647e6cdd6f2");
                    var actualRelatedObservable2 = actualRelatedObservables[1];
                    assert.instanceOf(actualRelatedObservable2, Observable);
                    assert.equal(actualRelatedObservable2.id, "purple-secure-systems:observable-1fb0e40b-d23d-4b81-ab78-0824e2642ebf");
                    var actualRelatedObservable3 = actualRelatedObservables[2];
                    assert.instanceOf(actualRelatedObservable3, Observable);
                    assert.equal(actualRelatedObservable3.id, "purple-secure-systems:observable-9db11783-3887-4f32-9f10-f18ebf2fba98");
                }
            }
        }
    });
});

