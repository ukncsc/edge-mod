define([
    "intern!object",
    "intern/chai!assert",
    "stix/objectTypes/StixObjectType",
    "stix/ReviewValue",
    "stix/StixPackage",
    "intern/dojo/text!./data/Observable_package_http_session.json"
], function (registerSuite, assert, StixObjectType, ReviewValue, StixPackage, package01) {
    "use strict";

    // statics go here
    var packageData = Object.freeze({
        "pss:observable-07130bf0-3aca-4c20-8dec-d6f3ac858bb4": Object.freeze(JSON.parse(package01))
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
            name: "stix/objectTypes/HttpSession",
            setup: function () {
                loadPackage("pss:observable-07130bf0-3aca-4c20-8dec-d6f3ac858bb4");
            },
            "is not null": function () {
                assert.isNotNull(classUnderTest);
            },
            "has correct properties": function () {
                var expectedProperties = [
                    {"label": "User Agent", "value": "MSIE/6.0"}
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
