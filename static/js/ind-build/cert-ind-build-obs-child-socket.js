define([
    "dcl/dcl",
    "ind-build/indicator-builder-shim",
    "ind-build/builder-shim",
    "ind-build/validation",
    "knockout"
], function (declare, indicator_builder, builder, validation, ko) {
    "use strict";

    var ChildSocket = declare(null, {
        declaredClass: "Child Socket",
        constructor: function () {
            this.port = ko.observable("");
            this.protocol = ko.observable("");
            this.ip_address = ko.observable("");
            this.hostname = ko.observable("");
            this.reviewOnly = ko.observable(false);
        },

        load: function (data) {
            this.port(data["port"] || "");
            this.protocol(data["protocol"] || "");
            this.ip_address(data["ip_address"] || "");
            this.hostname(data["hostname"] || "");
        },

        doValidation: function () {
            var msgs = new builder.Messages()
            if (!this.port()) {
                msgs.addError("Port is required");
            }
            if (!(this.ip_address() || this.hostname())) {
                msgs.addError("One of IP address or hostname is required");
            }
            if (this.ip_address() && this.hostname()) {
                msgs.addError("Enter IP address OR hostname, not both");
            }
            return msgs;
        },


        save: function () {
            return {
                port: this.port(),
                protocol: this.protocol(),
                ip_address: this.ip_address(),
                hostname: this.hostname()
            }
        }

    });
    return ChildSocket;
});
