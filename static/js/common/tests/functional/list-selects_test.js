define([
    "intern!object",
    "intern/chai!assert",
    "common/cert-build-list-selects"
], function (registerSuite, assert, classUnderTest) {
    "use strict";

    // statics go here

    registerSuite({
        name: 'listselect',

        'left populated': function () {
            return this.remote
                .get(require.toUrl('dummy-list.html'))
                .setFindTimeout(5000)
                .findById('list_selects_left')
                .getAttribute('options')
                .then(function (options) {
                    assert.strictEqual(options.length, 4);
                });

        }
    });
});