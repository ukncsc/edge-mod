define([
    "intern!object",
    "intern/chai!assert",
    "stix/objectTypes/StixObjectType",
    "stix/ReviewValue",
    "stix/StixPackage",
    "intern/dojo/text!./data/Observable_package_01.json",
    "intern/dojo/text!./data/Observable_package_02.json",
    "intern/dojo/text!./data/Observable_package_03.json"
], function (registerSuite, assert, StixObjectType, ReviewValue, StixPackage, package01, package02, package03) {
    "use strict";

    // statics go here
    var packageData = Object.freeze({
        "fireeye:observable-f44badfb-1c6a-4e15-87da-307dc9fc4239": Object.freeze(JSON.parse(package01)),
        "fireeye:observable-fa0607af-d668-4274-8010-dd70b025c4bd": Object.freeze(JSON.parse(package02)),
        "fireeye:observable-b850c92f-fb54-441f-b0e8-45ff7a897b87": Object.freeze(JSON.parse(package03))
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
            name: "stix/objectTypes/StixObjectType",
            "with custom properties": {
                setup: function () {
                    loadPackage("fireeye:observable-f44badfb-1c6a-4e15-87da-307dc9fc4239");
                },
                "is not null": function () {
                    assert.isNotNull(classUnderTest);
                },
                "has correct properties": function () {
                    var expectedProperties = [
                        {"label": "String Property", "value": "Hello, world"},
                        {"label": "Number Property", "value": 42},
                        {"label": "Boolean Property", "value": true},
                        {"label": "PIVY Password", "value": "pa55w0rd"},
                        {"label": "PIVY Username", "value": "admin"}
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
            "without custom properties": {
                setup: function () {
                    loadPackage("fireeye:observable-fa0607af-d668-4274-8010-dd70b025c4bd");
                },
                "is not null": function () {
                    assert.isNotNull(classUnderTest);
                },
                "has correct properties": function () {
                    var expectedProperties = [
                        {"label": "String Property", "value": "Curly, Larry and Moe"},
                        {"label": "Number Property", "value": 4242},
                        {"label": "Boolean Property", "value": false}
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
            "without any properties": {
                setup: function () {
                    loadPackage("fireeye:observable-b850c92f-fb54-441f-b0e8-45ff7a897b87");
                },
                "is not null": function () {
                    assert.isNotNull(classUnderTest);
                },
                "has correct properties": function () {
                    var actualProperties = classUnderTest.properties();
                    assert.isArray(actualProperties);
                    assert.lengthOf(actualProperties, 0);
                }
            }
        }
    });
});
