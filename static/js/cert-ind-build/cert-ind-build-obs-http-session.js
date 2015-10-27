define([
    "dcl/dcl",
    "cert-ind-build/indicator-builder-shim",
    "cert-ind-build/validation",
    "knockout"
], function (declare, indicator_builder, validation, ko) {
    "use strict";

    var CERTObservableHTTPSession = declare(indicator_builder.AbstractObservable, {
        constructor: declare.superCall(function (sup) {
            return function () {
                sup.call(this, "HTTP Session");
                this.user_agent = ko.observable("");
                this.user_agent.extend({
                    validate: {
                        "isValidCallback": validation.isNotEmpty,
                        "failedValidationMessage": "A user agent is required."
                    }
                }).valueHasMutated();
            }
        }),

        load: declare.superCall(function (sup) {
            return function(data) {
                sup.call(this, data);
                this.user_agent(data["user_agent"] || "");
            };
        }),

        doValidation: declare.superCall(function (sup) {
            return function () {
                var msgs = sup.call(this);
                if (this.user_agent.hasError()) {
                    msgs.addError(this.user_agent.errorMessage());
                }
                return msgs;
            };
        }),

        save: declare.superCall(function (sup) {
            return function () {
                if (this.objectTitle().length === 0) {
                    this.objectTitle(this.objectType() + " : " + this.user_agent());
                }
                return ko.utils.extend(sup.call(this), {
                    user_agent: this.user_agent()
                })
            };
        })
    });
    indicator_builder.ObservableHTTPSession = CERTObservableHTTPSession;
    return CERTObservableHTTPSession;
});
