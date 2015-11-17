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
            "constructor: no value, no state/message": {
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
            "constructor: error message": {
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
            "constructor: warning message": {
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
            "constructor: info message": {
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
            "constructor: missing message": {
                setup: function () {
                    classUnderTest = new ReviewValue("aValue", ReviewValue.State.INFO);
                },
                "value is 'aValue'": function () {
                    assert.equal(classUnderTest.value(), "aValue");
                },
                "state is INFO": function () {
                    assert.equal(classUnderTest.state(), ReviewValue.State.INFO);
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
                "hasInfo is true": function () {
                    assert.isTrue(classUnderTest.hasInfo());
                }
            },
            "constructor: invalid state (out of range)": {
                setup: function () {
                    classUnderTest = new ReviewValue("aValue", 42, "a message");
                },
                "value is 'aValue'": function () {
                    assert.equal(classUnderTest.value(), "aValue");
                },
                "state is OK": function () {
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
            "constructor: invalid state (NaN)": {
                setup: function () {
                    classUnderTest = new ReviewValue("aValue", NaN, "a message");
                },
                "value is 'aValue'": function () {
                    assert.equal(classUnderTest.value(), "aValue");
                },
                "state is OK": function () {
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
            "constructor: boolean value": {
                setup: function () {
                    classUnderTest = new ReviewValue(true);
                },
                "value is true": function () {
                    assert.isTrue(classUnderTest.value());
                },
                "isEmpty is false": function () {
                    assert.isFalse(classUnderTest.isEmpty());
                }
            },
            "constructor: non-finite numeric value": {
                setup: function () {
                    classUnderTest = new ReviewValue(NaN);
                },
                "value is null": function () {
                    assert.isNull(classUnderTest.value());
                },
                "isEmpty is true": function () {
                    assert.isTrue(classUnderTest.isEmpty());
                }
            },
            "constructor: finite numeric value": {
                setup: function () {
                    classUnderTest = new ReviewValue(42);
                },
                "value is 42": function () {
                    assert.equal(classUnderTest.value(), 42);
                },
                "isEmpty is false": function () {
                    assert.isFalse(classUnderTest.isEmpty());
                }
            },
            "constructor: empty string value": {
                setup: function () {
                    classUnderTest = new ReviewValue("");
                },
                "value is null": function () {
                    assert.isNull(classUnderTest.value());
                },
                "isEmpty is true": function () {
                    assert.isTrue(classUnderTest.isEmpty());
                }
            },
            "constructor: string value": {
                setup: function () {
                    classUnderTest = new ReviewValue("aValue");
                },
                "value is 'aValue'": function () {
                    assert.equal(classUnderTest.value(), "aValue");
                },
                "isEmpty is false": function () {
                    assert.isFalse(classUnderTest.isEmpty());
                }
            },
            "constructor: empty array value": {
                setup: function () {
                    classUnderTest = new ReviewValue([]);
                },
                "value is null": function () {
                    assert.isNull(classUnderTest.value());
                },
                "isEmpty is true": function () {
                    assert.isTrue(classUnderTest.isEmpty());
                }
            },
            "constructor: single array value (object)": {
                setup: function () {
                    classUnderTest = new ReviewValue([{ "a": "Curly" }]);
                },
                "value is [{\"a\": \"Curly\"}]": function () {
                    assert.deepEqual(classUnderTest.value(), [{"a": "Curly"}]);
                },
                "isEmpty is false": function () {
                    assert.isFalse(classUnderTest.isEmpty());
                }
            },
            "constructor: single array value, (non-object)": {
                setup: function () {
                    classUnderTest = new ReviewValue(["Curly"]);
                },
                "value is 'Curly'": function () {
                    assert.equal(classUnderTest.value(), "Curly");
                },
                "isEmpty is false": function () {
                    assert.isFalse(classUnderTest.isEmpty());
                }
            },
            "constructor: multiple array value (object)": {
                setup: function () {
                    classUnderTest = new ReviewValue([{"a": "Curly"}, {"b": "Larry"}, {"c": "Mo"}]);
                },
                "value is [{\"a\": \"Curly\"}, {\"b\": \"Larry\"}, {\"c\": \"Mo\"}]": function () {
                    assert.deepEqual(classUnderTest.value(), [{"a": "Curly"}, {"b": "Larry"}, {"c": "Mo"}]);
                },
                "isEmpty is false": function () {
                    assert.isFalse(classUnderTest.isEmpty());
                }
            },
            "constructor: multiple array value (non-object)": {
                setup: function () {
                    classUnderTest = new ReviewValue(["Curly", "Larry", "Mo"]);
                },
                "value is 'Curly, Larry and Mo'": function () {
                    assert.equal(classUnderTest.value(), "Curly, Larry and Mo");
                },
                "isEmpty is false": function () {
                    assert.isFalse(classUnderTest.isEmpty());
                }
            },
            "constructor: empty object value": {
                setup: function () {
                    classUnderTest = new ReviewValue({
                        value: ""
                    });
                },
                "value is null": function () {
                    assert.isNull(classUnderTest.value(), null);
                },
                "isEmpty is true": function () {
                    assert.isTrue(classUnderTest.isEmpty());
                }
            },
            "constructor: simple object value with custom delimiter": {
                setup: function () {
                    classUnderTest = new ReviewValue({
                        value: "aValue##delim##bValue",
                        delimiter: "##delim##"
                    });
                },
                "value is 'aValue,bValue'": function () {
                    assert.equal(classUnderTest.value(), "aValue,bValue");
                },
                "isEmpty is false": function () {
                    assert.isFalse(classUnderTest.isEmpty());
                }
            },
            "constructor: ranged object value": {
                setup: function () {
                    classUnderTest = new ReviewValue({
                        value: ["125.141.33.100", "125.141.33.200"],
                        condition: "inclusiveBetween",
                        apply_condition: "ANY"
                    });
                },
                "value is 'Any Inclusive Between 125.141.33.100 and 125.141.33.200'": function () {
                    assert.equal(classUnderTest.value(), "Any Inclusive Between 125.141.33.100 and 125.141.33.200");
                },
                "isEmpty is false": function () {
                    assert.isFalse(classUnderTest.isEmpty());
                }
            },
            "constructor: unknown type value": {
                setup: function () {
                    classUnderTest = new ReviewValue(new Date(Date.UTC(2015, 10, 9)));
                },
                "value is 'Mon Nov 09 2015 00:00:00 GMT+0000 (GMT)'": function () {
                    assert.equal(classUnderTest.value(), "Mon Nov 09 2015 00:00:00 GMT+0000 (GMT)");
                },
                "isEmpty is false": function () {
                    assert.isFalse(classUnderTest.isEmpty());
                }
            },
            "State.parse()": {
                "missing": function () {
                    assert.throws(
                        function () {
                            ReviewValue.State.parse();
                        },
                        "Invalid state: undefined"
                    );
                },
                "invalid": function () {
                    assert.throws(
                        function () {
                            ReviewValue.State.parse("BAD");
                        },
                        "Invalid state: BAD"
                    );
                },
                "OK": function () {
                    assert.equal(ReviewValue.State.parse("OK"), ReviewValue.State.OK);
                },
                "INFO": function () {
                    assert.equal(ReviewValue.State.parse("INFO"), ReviewValue.State.INFO);
                },
                "WARN": function () {
                    assert.equal(ReviewValue.State.parse("WARN"), ReviewValue.State.WARN);
                },
                "ERROR": function () {
                    assert.equal(ReviewValue.State.parse("ERROR"), ReviewValue.State.ERROR);
                }
            }
        }
    });
});
