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
            "constructor: valid (embedded name, simple value)": {
                setup: function () {
                    classUnderTest = new NamedProperty({ value: "embedded_name" }, "simple value");
                },
                "name()": function () {
                    assert.equal(classUnderTest.name(), "Embedded Name");
                },
                "value()": function () {
                    var actual = classUnderTest.value();
                    assert.equal(actual.value(), "simple value");
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
                    var actual = classUnderTest.value();
                    assert.equal(actual.value(), "embedded value");
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
                    var actual = classUnderTest.value();
                    assert.equal(actual.value(), "embedded value");
                }
            },
            "addToPropertyList()": {
                setup: function () {
                    propertyList = [];
                },
                "no property list": function () {
                    assert.throws(
                        function () {
                            NamedProperty.addToPropertyList(null, "name", "value");
                        },
                        "aPropertyList must be an array"
                    );
                },
                "no name": function () {
                    assert.throws(
                        function () {
                            NamedProperty.addToPropertyList(propertyList, null, "value");
                        },
                        "name must be a string"
                    );
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
            },
            "removeFromPropertyList()": {
                beforeEach: function () {
                    propertyList = [];
                    NamedProperty.addToPropertyList(propertyList, "label0", "value0");
                    NamedProperty.addToPropertyList(propertyList, "label1", "value1");
                    NamedProperty.addToPropertyList(propertyList, "label2", "value2");
                    assert.lengthOf(propertyList, 3);
                },
                "no property list": function () {
                    assert.throws(
                        function () {
                            NamedProperty.removeFromPropertyList(null, "name");
                        },
                        "aPropertyList must be an array"
                    );
                },
                "no name": function () {
                    assert.throws(
                        function () {
                            NamedProperty.removeFromPropertyList(propertyList, null);
                        },
                        "name must be a string"
                    );
                },
                "name not found": function () {
                    NamedProperty.removeFromPropertyList(propertyList, "not there");
                    assert.lengthOf(propertyList, 3);
                },
                "name found idx=0, match case": function () {
                    NamedProperty.removeFromPropertyList(propertyList, "Label0");
                    assert.lengthOf(propertyList, 2);
                    assert.equal(propertyList[0].label(), "Label1");
                    assert.equal(propertyList[1].label(), "Label2");
                },
                "name found idx=1, case insensitive": function () {
                    NamedProperty.removeFromPropertyList(propertyList, "label1");
                    assert.lengthOf(propertyList, 2);
                    assert.equal(propertyList[0].label(), "Label0");
                    assert.equal(propertyList[1].label(), "Label2");
                }
            }
        }
    });
});
