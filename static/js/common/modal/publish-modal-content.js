define([
    "dcl/dcl",
    "knockout"
], function (dcl, ko) {
    "use strict";

    function PublishModalContent() {
        this.message = ko.observable("");
        this.status = ko.observable("OK");
        this.validations = null;
        this.waitingForResponse = ko.observable(false);
        this.clientErrors = ko.observableArray([]);
        this.responseType = ko.observable(null);
        this.statusMessage = ko.computed(function () {
            return this.messagesByStatus[this.status()];
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

    PublishModalContent.prototype.messagesByStatus = {
        "FAILED": "Unable to publish this incident",
        "ERROR": "This incident has errors and cannot be published",
        "WARNING": "This incident has warnings",
        "INFO": "",
        "OK": ""
    }

    return PublishModalContent;
});