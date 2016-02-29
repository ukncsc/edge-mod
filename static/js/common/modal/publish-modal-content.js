define([
    "dcl/dcl",
    "knockout"
], function (dcl, ko) {
    "use strict";

    function PublishModalContent(type) {
        this.message = ko.observable("");
        this.status = ko.observable("OK");
        this.validations = null;
        this.waitingForResponse = ko.observable(false);
        this.clientErrors = ko.observableArray([]);
        this.responseType = ko.observable(null);
        this.statusMessage = ko.computed(function () {
            return this.getMessagesByStatus(this.status(), type);
        }, this);
        this.hasErrors = ko.computed(function () {
            return this.status() === "FAILED" || this.status() === "ERROR";
        }, this);
        this.hasWarnings = ko.computed(function () {
            return this.status() === "WARNING";
        }, this);
        this.hasInfos = ko.computed(function () {
            return this.status() === "INFO";
        }, this);
    }

    PublishModalContent.prototype.getMessagesByStatus = function (status, type) {
        if (status === "FAILED") {
            return "Unable to publish this " + type;
        }

        if (status === "ERROR") {
            return "This " + type + " has errors and cannot be published";
        }

        if (status === "WARNING") {
            return "This " + type + "  warnings";
        }

        return "";
    };

    return PublishModalContent;
});