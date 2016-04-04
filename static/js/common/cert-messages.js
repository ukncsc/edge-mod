define([
    "knockout",
    "dcl/dcl"
], function (ko, declare) {
    "use strict";

    return declare(null, {
        declaredClass: "Messages",

        constructor: function () {
            this.errors = ko.observableArray([]);
            this.warnings = ko.observableArray([]);

            this.displayErrors = ko.computed(function () {
                var limit = 6;
                var errorsToDisplay = this.errors();
                if (errorsToDisplay.length > limit) {
                    errorsToDisplay = errorsToDisplay.slice(0, limit);
                    errorsToDisplay.push("... and " + (this.errors().length - limit) + " others ...");
                }
                return errorsToDisplay;
            }, this);
        },

        addError: function (message) {
            this.errors.push(message);
        },

        hasErrors: function () {
            return this.errors().length > 0;
        },

        addWarning: function (message) {
            this.warnings.push(message);
        },

        hasWarnings: function () {
            return this.warnings().length > 0;
        },

        addMessages: function (messages) {
            this.errors(this.errors.peek().concat(messages.errors()));
            this.warnings(this.warnings.peek().concat(messages.warnings()));
        },

        hasMessages: function () {
            return this.hasErrors() || this.hasWarnings();
        }
    })
});

