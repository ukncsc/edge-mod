define([
    "intern!object",
    "intern/chai!assert",
    "stix/objectTypes/StixObjectType",
    "stix/ReviewValue",
    "stix/StixPackage",
    "intern/dojo/text!./data/Observable_package_registry.json",
    "stix/tests/unit/CreateEdges"
], function (registerSuite, assert, StixObjectType, ReviewValue, StixPackage, package01, CreateEdges) {
    "use strict";

    // statics go here
    var packageData = Object.freeze({
        "purple-secure-systems:Package-c324c477-f4e4-47b6-a0fc-6754ddc089b7": Object.freeze(JSON.parse(package01))
    });

    return registerSuite(function () {

        // suite variables go here
        var stixPackage = null;
        var classUnderTest = null;

        function loadPackage(rootId, objectId) {
            stixPackage = new StixPackage(packageData[rootId], objectId || rootId, [], {}, CreateEdges.createEdges([
                    "purple-secure-systems:Package-c324c477-f4e4-47b6-a0fc-6754ddc089b7",
                    "purple-secure-systems:observable-84519300-e075-4788-91b3-68af827e1fd0",
                    "purple-secure-systems:observable-00a48e2e-800d-445e-8431-92f597b0686f"
                ]));
            classUnderTest = stixPackage.root;
        }

        return {
            name: "stix/objectTypes/WindowsRegistryKey",
            "with key values" : {
                setup: function () {
                    loadPackage(
                        "purple-secure-systems:Package-c324c477-f4e4-47b6-a0fc-6754ddc089b7",
                        "purple-secure-systems:observable-84519300-e075-4788-91b3-68af827e1fd0"
                    );
                },
                "is not null": function () {
                    assert.isNotNull(classUnderTest);
                },
                "has correct properties": function () {
                    var expectedProperties = [
                        {"label": "Hive", "value": "HKEY_LOCAL_MACHINE\\Software"},
                        {"label": "Key", "value": "\\Microsoft\\Windows\\CurrentVersion\\Run"},
                        {"label": "BOTNET", "value": "C:\\BotNet.exe -serve C:\\"},
                        {"label": "KEYLOGGER", "value": "C:\\KeyLogger.exe"}
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
            },
            "without key values" : {
                setup: function () {
                    loadPackage(
                        "purple-secure-systems:Package-c324c477-f4e4-47b6-a0fc-6754ddc089b7",
                        "purple-secure-systems:observable-00a48e2e-800d-445e-8431-92f597b0686f"
                    );
                },
                "is not null": function () {
                    assert.isNotNull(classUnderTest);
                },
                "has correct properties": function () {
                    var expectedProperties = [
                        {"label": "Hive", "value": "HKEY_LOCAL_MACHINE\\Software"},
                        {"label": "Key", "value": "\\Microsoft\\Windows\\CurrentVersion\\RunOnce"}
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
        }
    });
});
