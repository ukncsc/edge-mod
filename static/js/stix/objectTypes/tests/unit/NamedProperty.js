define([
    "intern!object",
    "intern/chai!assert",
    "stix/ReviewValue",
    "../../NamedProperty"
], function (registerSuite, assert, ReviewValue, NamedProperty) {
    "use strict";

    // statics go here

    return registerSuite(function () {

        // suite variables go here
        var classUnderTest = null;
        var propertyList = null;

        return {
            name: "stix/objectTypes/NamedProperty",
            "constructor: missing name": function () {
                assert.throws(
                    function () {
                        new NamedProperty(null, null);
                    },
                    "name must be a string"
                );
            },
            "constructor: valid (simple name and value)": {
                setup: function () {
                    classUnderTest = new NamedProperty("simple_name", "simple value");
                },
                "name()": function () {
                    assert.equal(classUnderTest.name(), "Simple Name");
                },
                "value()": function () {
                    var actual = classUnderTest.value();
                    assert.equal(actual.value(), "simple value");
                }
            },
/* TODO: work out what's still needed here
            "constructor: valid (embedded name, simple value)": {
                setup: function () {
                    classUnderTest = new NamedProperty({ value: "embedded_name" }, "simple value");
                },
                "name()": function () {
                    assert.equal(classUnderTest.name(), "Embedded Name");
                },
                "value()": function () {
                    assert.equal(classUnderTest.value(), "simple value");
                }
            },
            "constructor: valid (simple name, embedded value)": {
                setup: function () {
                    classUnderTest = new NamedProperty("simple_name", { value: "embedded value" });
                },
                "name()": function () {
                    assert.equal(classUnderTest.name(), "Simple Name");
                },
                "value()": function () {
                    assert.equal(classUnderTest.value(), "embedded value");
                }
            },
            "constructor: valid (embedded name and value)": {
                setup: function () {
                    classUnderTest = new NamedProperty({ value: "embedded_name" }, { value: "embedded value" });
                },
                "name()": function () {
                    assert.equal(classUnderTest.name(), "Embedded Name");
                },
                "value()": function () {
                    assert.equal(classUnderTest.value(), "embedded value");
                }
            },
*/
            "addToPropertyList()": {
                setup: function () {
                    propertyList = [];
                },
                "no value": function () {
                    NamedProperty.addToPropertyList(propertyList, "name", null);
                    assert.lengthOf(propertyList, 0);
                },
                "with value": function () {
                    NamedProperty.addToPropertyList(propertyList, "name", "value");
                    assert.lengthOf(propertyList, 1);
                    var actualProperty = propertyList[0];
                    assert.equal(actualProperty.label(), "Name");
                    var actual = actualProperty.value();
                    assert.instanceOf(actual, ReviewValue);
                    assert.isFalse(actual.isEmpty());
                    assert.equal(actual.value(), "value");
                }
            }
        }
    });
});
