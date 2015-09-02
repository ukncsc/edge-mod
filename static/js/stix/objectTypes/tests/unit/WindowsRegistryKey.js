define([
    "intern!object",
    "intern/chai!assert",
    "stix/objectTypes/StixObjectType",
    "stix/StixPackage",
    "intern/dojo/text!./data/Observable_package_registry.json"
], function (registerSuite, assert, StixObjectType, StixPackage, package01) {
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
            stixPackage = new StixPackage(packageData[rootId], objectId || rootId);
            classUnderTest = stixPackage.root;
        }

        return {
            name: "stix/objectTypes/File",
            "with hashes" : {
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
                    assert.deepEqual(classUnderTest.properties(), [
                        { "label": "Hive", "value": "HKEY_LOCAL_MACHINE\\Software" },
                        { "label": "Key", "value": "\\Microsoft\\Windows\\CurrentVersion\\Run" },
                        { "label": "BOTNET", "value": "C:\\BotNet.exe -serve C:\\" },
                        { "label": "KEYLOGGER", "value": "C:\\KeyLogger.exe" }
                    ]);
                }
            },
            "without hashes" : {
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
                    assert.deepEqual(classUnderTest.properties(), [
                        { "label": "Hive", "value": "HKEY_LOCAL_MACHINE\\Software" },
                        { "label": "Key", "value": "\\Microsoft\\Windows\\CurrentVersion\\RunOnce" }
                    ]);
                }
            }
        }
    });
});
