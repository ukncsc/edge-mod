define([
    "dcl/dcl",
    "knockout",
    "ind-build/indicator-builder-shim",
    "ind-build/validation"
], function (declare, ko, indicator_builder, validation) {
    "use strict";

    var CERTObservablePort = declare(indicator_builder.AbstractObservable, {
        constructor: declare.superCall(function (sup) {
            return function () {
                sup.call(this, "Port");
                this.port = ko.observable("");
                this.port.extend({
                    validate: {
                        "isValidCallback": validation.isNotEmpty,
                        "failedValidationMessage": "A port value is required"
                    }
                }).valueHasMutated();
                this.protocol = ko.observable("");
            }
        }),

        load: declare.superCall(function (sup) {
            return function (data) {
                sup.call(this, data);
                this.port(data["port_value"]|| "");
                this.protocol(data["layer4_protocol"] || "");
            };
        }),

        doValidation: declare.superCall(function (sup) {
            return function () {
                var msgs = sup.call(this);
                if (this.port.hasError()) {
                    msgs.addError(this.port.errorMessage());
                }
                return msgs;
            };
        }),

        save: declare.superCall(function (sup) {
            return function () {
                if (this.objectTitle().length === 0) {
                    this.objectTitle(this.objectType() + " : " + this.port() + " : " + this.protocol());
                }
                return ko.utils.extend(sup.call(this), {
                        port_value: this.port(),
                        layer4_protocol: this.protocol()
                })
            };
        })
    });

    indicator_builder.ObservablePort = CERTObservablePort;
    return CERTObservablePort;
});

