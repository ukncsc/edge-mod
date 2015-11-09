define([
    "intern!object",
    "intern/chai!assert",
    "stix/ReviewValue"
], function (registerSuite, assert, ReviewValue) {
    "use strict";

    // statics go here

    return registerSuite(function () {

        // suite variables go here
        var classUnderTest = null;

        return {
            name: "stix/ReviewValue",
            "no value, no state/message": {
                setup: function () {
                    classUnderTest = new ReviewValue();
                },
                "value is null": function () {
                    assert.isNull(classUnderTest.value());
                },
                "state is OK": function () {
                    assert.equal(classUnderTest.state(), ReviewValue.State.OK);
                },
                "message is null": function () {
                    assert.isNull(classUnderTest.message());
                },
                "isEmpty is true": function () {
                    assert.isTrue(classUnderTest.isEmpty());
                },
                "hasError is false": function () {
                    assert.isFalse(classUnderTest.hasError());
                },
                "hasWarning is false": function () {
                    assert.isFalse(classUnderTest.hasWarning());
                },
                "hasInfo is false": function () {
                    assert.isFalse(classUnderTest.hasInfo());
                }
            },
            "string value, no state/message": {
                setup: function () {
                    classUnderTest = new ReviewValue("aValue");
                },
                "value is 'aValue'": function () {
                    assert.equal(classUnderTest.value(), "aValue");
                },
                "state is OK": function () {
                    assert.equal(classUnderTest.state(), ReviewValue.State.OK);
                },
                "message is null": function () {
                    assert.isNull(classUnderTest.message());
                },
                "isEmpty is false": function () {
                    assert.isFalse(classUnderTest.isEmpty());
                },
                "hasError is false": function () {
                    assert.isFalse(classUnderTest.hasError());
                },
                "hasWarning is false": function () {
                    assert.isFalse(classUnderTest.hasWarning());
                },
                "hasInfo is false": function () {
                    assert.isFalse(classUnderTest.hasInfo());
                }
            },
            "string value, error message": {
                setup: function () {
                    classUnderTest = new ReviewValue("aValue", ReviewValue.State.ERROR, "error message");
                },
                "value is 'aValue'": function () {
                    assert.equal(classUnderTest.value(), "aValue");
                },
                "state is ERROR": function () {
                    assert.equal(classUnderTest.state(), ReviewValue.State.ERROR);
                },
                "message is 'error message'": function () {
                    assert.equal(classUnderTest.message(), "error message");
                },
                "isEmpty is false": function () {
                    assert.isFalse(classUnderTest.isEmpty());
                },
                "hasError is true": function () {
                    assert.isTrue(classUnderTest.hasError());
                },
                "hasWarning is false": function () {
                    assert.isFalse(classUnderTest.hasWarning());
                },
                "hasInfo is false": function () {
                    assert.isFalse(classUnderTest.hasInfo());
                }
            },
            "string value, warning message": {
                setup: function () {
                    classUnderTest = new ReviewValue("aValue", ReviewValue.State.WARN, "warning message");
                },
                "value is 'aValue'": function () {
                    assert.equal(classUnderTest.value(), "aValue");
                },
                "state is WARN": function () {
                    assert.equal(classUnderTest.state(), ReviewValue.State.WARN);
                },
                "message is 'warning message'": function () {
                    assert.equal(classUnderTest.message(), "warning message");
                },
                "isEmpty is false": function () {
                    assert.isFalse(classUnderTest.isEmpty());
                },
                "hasError is false": function () {
                    assert.isFalse(classUnderTest.hasError());
                },
                "hasWarning is true": function () {
                    assert.isTrue(classUnderTest.hasWarning());
                },
                "hasInfo is false": function () {
                    assert.isFalse(classUnderTest.hasInfo());
                }
            },
            "string value, info message": {
                setup: function () {
                    classUnderTest = new ReviewValue("aValue", ReviewValue.State.INFO, "info message");
                },
                "value is 'aValue'": function () {
                    assert.equal(classUnderTest.value(), "aValue");
                },
                "state is INFO": function () {
                    assert.equal(classUnderTest.state(), ReviewValue.State.INFO);
                },
                "message is 'info message'": function () {
                    assert.equal(classUnderTest.message(), "info message");
                },
                "isEmpty is false": function () {
                    assert.isFalse(classUnderTest.isEmpty());
                },
                "hasError is false": function () {
                    assert.isFalse(classUnderTest.hasError());
                },
                "hasWarning is false": function () {
                    assert.isFalse(classUnderTest.hasWarning());
                },
                "hasInfo is true": function () {
                    assert.isTrue(classUnderTest.hasInfo());
                }
            },
            "string value, invalid state": {
                setup: function () {
                    classUnderTest = new ReviewValue("aValue", 42, "a message");
                },
                "value is 'aValue'": function () {
                    assert.equal(classUnderTest.value(), "aValue");
                },
                "state is INFO": function () {
                    assert.equal(classUnderTest.state(), ReviewValue.State.OK);
                },
                "message is 'info message'": function () {
                    assert.isNull(classUnderTest.message());
                },
                "isEmpty is false": function () {
                    assert.isFalse(classUnderTest.isEmpty());
                },
                "hasError is false": function () {
                    assert.isFalse(classUnderTest.hasError());
                },
                "hasWarning is false": function () {
                    assert.isFalse(classUnderTest.hasWarning());
                },
                "hasInfo is false": function () {
                    assert.isFalse(classUnderTest.hasInfo());
                }
            },
            "boolean value, no state/message": {
                setup: function () {
                    classUnderTest = new ReviewValue(true);
                },
                "value is true": function () {
                    assert.isTrue(classUnderTest.value());
                },
                "state is OK": function () {
                    assert.equal(classUnderTest.state(), ReviewValue.State.OK);
                },
                "message is null": function () {
                    assert.isNull(classUnderTest.message());
                },
                "isEmpty is false": function () {
                    assert.isFalse(classUnderTest.isEmpty());
                },
                "hasError is false": function () {
                    assert.isFalse(classUnderTest.hasError());
                },
                "hasWarning is false": function () {
                    assert.isFalse(classUnderTest.hasWarning());
                },
                "hasInfo is false": function () {
                    assert.isFalse(classUnderTest.hasInfo());
                }
            },
            "non-finite numeric value, no state/message": {
                setup: function () {
                    classUnderTest = new ReviewValue(NaN);
                },
                "value is null": function () {
                    assert.isNull(classUnderTest.value());
                },
                "state is OK": function () {
                    assert.equal(classUnderTest.state(), ReviewValue.State.OK);
                },
                "message is null": function () {
                    assert.isNull(classUnderTest.message());
                },
                "isEmpty is true": function () {
                    assert.isTrue(classUnderTest.isEmpty());
                },
                "hasError is false": function () {
                    assert.isFalse(classUnderTest.hasError());
                },
                "hasWarning is false": function () {
                    assert.isFalse(classUnderTest.hasWarning());
                },
                "hasInfo is false": function () {
                    assert.isFalse(classUnderTest.hasInfo());
                }
            },
            "finite numeric value, no state/message": {
                setup: function () {
                    classUnderTest = new ReviewValue(42);
                },
                "value is 42": function () {
                    assert.equal(classUnderTest.value(), 42);
                },
                "state is OK": function () {
                    assert.equal(classUnderTest.state(), ReviewValue.State.OK);
                },
                "message is null": function () {
                    assert.isNull(classUnderTest.message());
                },
                "isEmpty is false": function () {
                    assert.isFalse(classUnderTest.isEmpty());
                },
                "hasError is false": function () {
                    assert.isFalse(classUnderTest.hasError());
                },
                "hasWarning is false": function () {
                    assert.isFalse(classUnderTest.hasWarning());
                },
                "hasInfo is false": function () {
                    assert.isFalse(classUnderTest.hasInfo());
                }
            },
            "empty array value, no state/message": {
                setup: function () {
                    classUnderTest = new ReviewValue([]);
                },
                "value is null": function () {
                    assert.isNull(classUnderTest.value());
                },
                "state is OK": function () {
                    assert.equal(classUnderTest.state(), ReviewValue.State.OK);
                },
                "message is null": function () {
                    assert.isNull(classUnderTest.message());
                },
                "isEmpty is true": function () {
                    assert.isTrue(classUnderTest.isEmpty());
                },
                "hasError is false": function () {
                    assert.isFalse(classUnderTest.hasError());
                },
                "hasWarning is false": function () {
                    assert.isFalse(classUnderTest.hasWarning());
                },
                "hasInfo is false": function () {
                    assert.isFalse(classUnderTest.hasInfo());
                }
            }
        }
    });
});
