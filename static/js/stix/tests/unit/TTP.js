define([
    "intern!object",
    "stix/TTP"
], function (registerSuite, TTP) {

    return registerSuite({
        name: "TTP",
        setup: function () {
            console.log('outer setup');
        },
        beforeEach: function () {
            console.log('outer beforeEach');
        },
        afterEach: function () {
            console.log('outer afterEach');
        },
        teardown: function () {
            console.log('outer teardown');
        },
        "passing test": function () {},
        "failing test": function () {
            throw new Error("Fail");
        }
    });
});
