define([
    "knockout"
], function (ko) {
    "use strict";

    function Messages() {
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
    }

    Messages.prototype.addError = function (message) {
        this.errors.push(message);
    };

    Messages.prototype.hasErrors = function () {
        return this.errors().length > 0;
    };

    Messages.prototype.addWarning = function (message) {
        this.warnings.push(message);
    };

    Messages.prototype.hasWarnings = function () {
        return this.warnings().length > 0;
    };

    Messages.prototype.addMessages = function (messages) {
        this.errors(this.errors.peek().concat(messages.errors()));
        this.warnings(this.warnings.peek().concat(messages.warnings()));
    };

    Messages.prototype.hasMessages = function () {
        return this.hasErrors() || this.hasWarnings();
    };

    return Messages;
});
