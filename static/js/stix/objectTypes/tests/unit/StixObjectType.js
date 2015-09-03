define([
    "intern!object",
    "intern/chai!assert",
    "stix/objectTypes/StixObjectType",
    "stix/StixPackage",
    "intern/dojo/text!./data/Observable_package_01.json"
], function (registerSuite, assert, StixObjectType, StixPackage, package01) {
    "use strict";

    // statics go here
    var packageData = Object.freeze({
        "fireeye:observable-f44badfb-1c6a-4e15-87da-307dc9fc4239": Object.freeze(JSON.parse(package01))
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
            name: "stix/objectTypes/StixObjectType",
            setup: function () {
                loadPackage("fireeye:observable-f44badfb-1c6a-4e15-87da-307dc9fc4239");
            },
            "is not null": function () {
                assert.isNotNull(classUnderTest);
            },
            "has correct properties": function () {
                assert.deepEqual(classUnderTest.properties(), [
                    { "label": "String Property", "value": "Hello, world" },
                    { "label": "Number Property", "value": 42 },
                    { "label": "PIVY Password", "value": "pa55w0rd" },
                    { "label": "PIVY Username", "value": "admin" }
                ]);
            }
        }
    });
});
