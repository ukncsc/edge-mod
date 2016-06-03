define([
    "dcl/dcl",
    "ind-build/indicator-builder-shim",
    "ind-build/validation",
    "knockout",
    "ind-build/cert-ind-build-obs-child-socket"
], function (declare, indicator_builder, validation, ko, ChildSocket) {
    "use strict";

    var CERTObservableNetworkConnection = declare(indicator_builder.AbstractObservable, {
        constructor: declare.superCall(function (sup) {
            return function () {
                sup.call(this, "Network Connection");
                this.source_socket_address = ko.observable(new ChildSocket);
                this.source_socket_address().reviewOnly = ko.computed(function () {
                    return this.reviewOnly();
                }, this);
                this.destination_socket_address = ko.observable(new ChildSocket);
                this.destination_socket_address().reviewOnly = ko.computed(function () {
                    return this.reviewOnly();
                }, this);
            }
        }),

        load: declare.superCall(function (sup) {
            return function (data) {
                sup.call(this, data);
                this.source_socket_address().load(data["source_socket_address"] || new ChildSocket);
                this.destination_socket_address().load(data["destination_socket_address"] || new ChildSocket);
            };
        }),

        doValidation: declare.superCall(function (sup) {
            return function () {
                var msgs = sup.call(this);
                this.mergeSocketValidation(msgs, this.source_socket_address().doValidation());
                this.mergeSocketValidation(msgs, this.destination_socket_address().doValidation())
                return msgs;
            };
        }),

        mergeSocketValidation: function (networkMessages, socketMessages) {
            var mergedErrors = networkMessages.errors().concat(socketMessages.errors());
            networkMessages.errors(mergedErrors);
        },

        generateSummary: function () {
            var title = this.objectType() + " : " + (this.source_socket_address().ip_address() || this.source_socket_address().hostname()) + ":" + this.source_socket_address().port();
            if (this.source_socket_address().protocol()) {
                title += " (" + this.source_socket_address().protocol() + ")";
            }
            title += " : " + (this.destination_socket_address().ip_address() || this.destination_socket_address().hostname()) + ":" + this.destination_socket_address().port();
            if (this.destination_socket_address().protocol()) {
                title += " (" + this.destination_socket_address().protocol() + ")";
            }
            return title.substring(0, 80);
        },

        save: declare.superCall(function (sup) {
            return function () {
                if (this.objectTitle().length === 0) {
                    this.objectTitle(this.generateSummary());
                }
                return ko.utils.extend(sup.call(this), {
                    source_socket_address: {
                        port: this.source_socket_address().port(),
                        protocol: this.source_socket_address().protocol(),
                        ip_address: this.source_socket_address().ip_address(),
                        hostname: this.source_socket_address().hostname()
                    },
                    destination_socket_address: {
                        port: this.destination_socket_address().port(),
                        protocol: this.destination_socket_address().protocol(),
                        ip_address: this.destination_socket_address().ip_address(),
                        hostname: this.destination_socket_address().hostname()
                    }
                })
            };
        })
    });

    indicator_builder.ObservableNetworkConnection = CERTObservableNetworkConnection;
    return CERTObservableNetworkConnection;
});
