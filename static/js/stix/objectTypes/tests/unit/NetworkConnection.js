define([
    "intern!object",
    "intern/chai!assert",
    "stix/objectTypes/StixObjectType",
    "stix/ReviewValue",
    "stix/StixPackage",
    "intern/dojo/text!./data/Observable_package_network_connection.json"
], function (registerSuite, assert, StixObjectType, ReviewValue, StixPackage, package01) {
    "use strict";

    // statics go here
    var packageData = Object.freeze({
        "pss:observable-a3ea4129-19e4-492a-ba47-0ddf4064f784": Object.freeze(JSON.parse(package01))
    });

    return registerSuite(function () {

        // suite variables go here
        var stixPackage = null;
        var classUnderTest = null;

        function loadPackage(rootId) {
            stixPackage = new StixPackage(packageData[rootId], rootId, [], {}, [{"id_":rootId, "ty":"obs"}]);
            classUnderTest = stixPackage.root;
        }

        return {
            name: "stix/objectTypes/NetworkConnection",
            setup: function () {
                loadPackage("pss:observable-a3ea4129-19e4-492a-ba47-0ddf4064f784");
            },
            "is not null": function () {
                assert.isNotNull(classUnderTest);
            },
            "has correct properties": function () {
                var expectedProperties = [
                    {"label": "Src IP", "value": "192.168.57.101"},
                    {"label": "Src Port", "value": "8443"},
                    {"label": "Src Protocol", "value": "https"},
                    {"label": "Dst Host", "value": "localhost"},
                    {"label": "Dst Port", "value": "87"},
                    {"label": "Dst Protocol", "value": "http"}

                ];
                var actualProperties = classUnderTest.properties();
                assert.isArray(actualProperties);
                assert.lengthOf(actualProperties, expectedProperties.length);
                actualProperties.forEach(function (actualProperty, idx) {
                    var expected = expectedProperties[idx];
                    assert.equal(actualProperty.label(), expected.label);
                    var actual = actualProperty.value();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty);
                    assert.equal(actual.value, expected.value);
                });
            }
        }
    });
});
