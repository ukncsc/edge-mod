define([
    "intern!object",
    "intern/chai!assert",
    "knockout",
    "common/change-tracker",
    "common/identity"
], function (registerSuite, assert, ko, ChangeTracker, Identity) {
    "use strict";

    // statics go here

    return registerSuite(function () {

        // suite variables go here

        return {
            name: "common/identity",
            "load data": {
                "isTrue": function () {
                    var identity = new Identity();
                    assert.isTrue(ko.ignoreComputeHash({ignoreComputeHash: true}));
                }
            }
        }
    });
});
