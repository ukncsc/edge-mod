if (typeof window === "undefined") {
    window = {};
}
define([
    "intern!object",
    "intern/chai!assert",
    "inc-build/cert-incident-builder-shim"
], function (registerSuite, assert, classUnderTest) {
    "use strict";

    // statics go here

    return registerSuite(function () {

        // suite variables go here

        return {
            name: "inc-build/cert-incident-builder-shim",
            "constructor": function () {
                assert.isDefined(classUnderTest);
                assert.isDefined(window.incident_builder);
                assert.equal(classUnderTest, window.incident_builder);
            }
        }
    });
});
