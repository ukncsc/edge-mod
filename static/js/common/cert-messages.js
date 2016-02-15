define([
    "../dcl/dcl",
    "knockout"
], function (declare, ko) {
    "use strict";

    function Messages () {
        this.errors = ko.observableArray([]);
        this.warnings = ko.observableArray([]);
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
