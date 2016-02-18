if (typeof window === "undefined") {
    window = {};
}
define([
    "intern!object",
    "intern/chai!assert",
    "inc-build/cert-inc-build-attributed-actors",
    "inc-build/cert-inc-build-discovery-methods",
    "inc-build/cert-inc-build-effects",
    "inc-build/cert-inc-build-general",
    "inc-build/cert-inc-build-intended-effects",
    "inc-build/cert-inc-build-leveraged-ttps",
    "inc-build/cert-inc-build-related-incidents",
    "inc-build/cert-inc-build-related-indicators",
    "inc-build/cert-inc-build-related-observables",
    "inc-build/cert-inc-build-trust-groups",
    "inc-build/cert-inc-build-victims",
    "inc-build/cert-inc-build-responders"
], function (registerSuite, assert) {
    "use strict";

    // statics go here

    return registerSuite(function () {

        // suite variables go here

        return {
            name: "inc-build/load-all-modules",
            "constructor": function () {

            }
        }
    });
});
