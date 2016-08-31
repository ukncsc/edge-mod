define([
    "intern!object",
    "intern/chai!assert",
    "stix/objectTypes/StixObjectType",
    "stix/ReviewValue",
    "stix/StixPackage",
    "intern/dojo/text!./data/Observable_package_socket_address_01.json",
    "intern/dojo/text!./data/Observable_package_socket_address_02.json"
], function (registerSuite, assert, StixObjectType, ReviewValue, StixPackage, package01, package02) {
    "use strict";

    // statics go here
    var packageData = Object.freeze({
        "pss:observable-aedfd423-0af1-42fc-a8c0-b4b71a6f94dd": Object.freeze(JSON.parse(package01)),
        "pss:observable-4daef1c0-f814-4d50-a500-f0db3a5f8535": Object.freeze(JSON.parse(package02))
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
            name: "stix/objectTypes/SocketAddress",
            "with IP address": {
                setup: function () {
                    loadPackage("pss:observable-aedfd423-0af1-42fc-a8c0-b4b71a6f94dd");
                },
                "is not null": function () {
                    assert.isNotNull(classUnderTest);
                },
                "has correct properties": function () {
                    var expectedProperties = [
                        {"label": "Ip Address", "value": "192.168.57.101"},
                        {"label": "Port", "value": 8443},
                        {"label": "Protocol", "value": "https"}
                    ];
                    var actualProperties = classUnderTest.properties();
                    assert.isArray(actualProperties);
                    assert.lengthOf(actualProperties, expectedProperties.length);
                    actualProperties.forEach(function (actualProperty, idx) {
                        var expected = expectedProperties[idx];
                        assert.equal(actualProperty.label(), expected.label);
                        var actual = actualProperty.value();
                        assert.instanceOf(actual, ReviewValue);
                        assert.isFalse(actual.isEmpty());
                        assert.equal(actual.value(), expected.value);
                    });
                }
            },
            "with hostname": {
                setup: function () {
                    loadPackage("pss:observable-4daef1c0-f814-4d50-a500-f0db3a5f8535");
                },
                "is not null": function () {
                    assert.isNotNull(classUnderTest);
                },
                "has correct properties": function () {
                    var expectedProperties = [
                        {"label": "Hostname", "value": "myserver.localdomain"},
                        {"label": "Port", "value": 8080},
                        {"label": "Protocol", "value": "http"}
                    ];
                    var actualProperties = classUnderTest.properties();
                    assert.isArray(actualProperties);
                    assert.lengthOf(actualProperties, expectedProperties.length);
                    actualProperties.forEach(function (actualProperty, idx) {
                        var expected = expectedProperties[idx];
                        assert.equal(actualProperty.label(), expected.label);
                        var actual = actualProperty.value();
                        assert.instanceOf(actual, ReviewValue);
                        assert.isFalse(actual.isEmpty());
                        assert.equal(actual.value(), expected.value);
                    });
                }
            }
        }
    });
});
