if (typeof window === "undefined") {
    window = {};
}
define([
    "intern!object",
    "intern/chai!assert",
    "ind-build/indicator-builder-shim"
], function (registerSuite, assert, classUnderTest) {
    "use strict";

    // statics go here

    return registerSuite(function () {

        // suite variables go here

        return {
            name: "ind-build/indicator-builder-shim",
            "constructor": function () {
                assert.isDefined(classUnderTest);
                assert.isDefined(window.indicator_builder);
                assert.equal(classUnderTest, window.indicator_builder);
            }
        }
    });
});
