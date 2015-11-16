define([
    "intern!object",
    "intern/chai!assert",
    "ind-build/validation"
], function (registerSuite, assert, classUnderTest) {
    "use strict";

    // statics go here

    return registerSuite(function () {

        // suite variables go here

        return {
            name: "ind-build/validation",
            "hasValue": {
                "has a value": function () {
                    assert.isTrue(classUnderTest.hasValue(" "));
                },
                "does not have a value": function () {
                    assert.isFalse(classUnderTest.hasValue(undefined));
                    assert.isFalse(classUnderTest.hasValue(null));
                    assert.isFalse(classUnderTest.hasValue(false));
                    assert.isFalse(classUnderTest.hasValue(""));
                    assert.isFalse(classUnderTest.hasValue(0));
                }
            },
            "isNotEmpty": {
                "is not empty": function () {
                    assert.isTrue(classUnderTest.isNotEmpty(" * "));
                },
                "is empty": function () {
                    assert.isFalse(classUnderTest.isNotEmpty(undefined));
                    assert.isFalse(classUnderTest.isNotEmpty(null));
                    assert.isFalse(classUnderTest.isNotEmpty(""));
                    assert.isFalse(classUnderTest.isNotEmpty(" "));
                    assert.isFalse(classUnderTest.isNotEmpty("\t"));
                }
            }
        }
    });
});
