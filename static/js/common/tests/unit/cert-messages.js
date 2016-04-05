define([
    "intern!object",
    "intern/chai!assert",
    "common/cert-messages"
], function (registerSuite, assert, Messages) {
    "use strict";

    return registerSuite(function () {

        return {
            name: "common/cert-messages",
            "constructor": function () {
                assert.isDefined(Messages);
            },
            "add warning": function () {
                var messages = new Messages();

                messages.addWarning("message");

                assert.isTrue(messages.hasWarnings());
            },
            "add error": function () {
                var messages = new Messages();

                messages.addError("error");

                assert.isTrue(messages.hasErrors());
            },
            "has message from error": function () {
                var messages = new Messages();

                messages.addError("error");

                assert.isTrue(messages.hasMessages());
            },
            "has message from warning": function () {
                var messages = new Messages();

                messages.addWarning("warning");

                assert.isTrue(messages.hasMessages());
            },
            "add message with warning and error": function () {
                var messages = new Messages();

                var messagesToAdd = new Messages();

                messagesToAdd.addError("error");
                messagesToAdd.addWarning("warning");

                messages.addMessages(messagesToAdd);

                assert.isTrue(messages.hasMessages());
            },
            "limits display errors to 6": function () {
                var messages = new Messages();

                messages.addError("error1");
                messages.addError("error2");
                messages.addError("error3");
                messages.addError("error4");
                messages.addError("error5");
                messages.addError("error6");
                messages.addError("error7");
                messages.addError("error8");
                messages.addError("error9");

                assert.equal(messages.displayErrors().length, 7, "Maximum number of errors are limited to 6");
            }

        }
    });
});

