define([
    "dcl/dcl",
    "ind-build/indicator-builder-shim",
    "ind-build/validation",
    "knockout"
], function (declare, indicator_builder, validation, ko) {
    "use strict";

    var CERTObservableNetworkConnection = declare(indicator_builder.AbstractObservable, {
            constructor: declare.superCall(function (sup) {
                return function () {
                    sup.call(this, "Network Connection");
                    this.source_socket_address = ko.observable(new indicator_builder.ObservableSocket);
                    this.destination_socket_address = ko.observable(new indicator_builder.ObservableSocket);
                }
            }),

            load: declare.superCall(function (sup) {
                return function (data) {
                    sup.call(this, data);
                    this.source_socket_address(data["source_socket_address"] || new indicator_builder.ObservableSocket);
                    this.destination_socket_address(data["destination_socket_address"] || new indicator_builder.ObservableSocket);
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

            save: declare.superCall(function (sup) {
                return function () {
                    if (this.objectTitle().length === 0) {
                        var title = this.objectType() + " : " + (this.source_socket_address().ip_address() || this.source_socket_address().hostname()) + ":" + this.source_socket_address().port();
                        if (this.source_socket_address().protocol()) {
                            title += " (" + this.source_socket_address().protocol() + ")";
                        }
                        title += " : " + (this.destination_socket_address().ip_address() || this.destination_socket_address().hostname()) + ":" + this.destination_socket_address().port();
                        if (this.destination_socket_address().protocol()) {
                            title += " (" + this.destination_socket_address().protocol() + ")";
                        }
                        this.objectTitle(title.substring(0, 80));
                    }
                    return ko.utils.extend(sup.call(this), {
                        source_socket_address: this.source_socket_address(),
                        destination_socket_address: this.destination_socket_address()
                    })
                };
            })
        })
        ;
    indicator_builder.ObservableNetworkConnection = CERTObservableNetworkConnection;
    return CERTObservableNetworkConnection;
})
;
