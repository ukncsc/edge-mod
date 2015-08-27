define([
    "intern!object",
    "intern/chai!assert",
    "../../NamedProperty"
], function (registerSuite, assert, NamedProperty) {
    "use strict";

    // statics go here

    return registerSuite(function () {

        // suite variables go here
        var classUnderTest = null;
        var propertyList = null;

        return {
            name: "NamedProperty",
            "constructor: missing name": function () {
                assert.throws(
                    function () {
                        new NamedProperty(null, null);
                    },
                    "name must be a string"
                );
            },
            "constructor: valid (simple value)": {
                setup: function () {
                    classUnderTest = new NamedProperty("a_name", "a value");
                },
                "name()": function () {
                    assert.equal(classUnderTest.name(), "A Name");
                },
                "value()": function () {
                    assert.equal(classUnderTest.value(), "a value");
                }
            },
            "constructor: valid (embedded value)": {
                setup: function () {
                    classUnderTest = new NamedProperty("another_name", { value: "embedded value" });
                },
                "name()": function () {
                    assert.equal(classUnderTest.name(), "Another Name");
                },
                "value()": function () {
                    assert.equal(classUnderTest.value(), "embedded value");
                }
            },
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
                    assert.deepEqual(propertyList[0], {label:"Name", value:"value"});
                }
            }
        }
    });
});
