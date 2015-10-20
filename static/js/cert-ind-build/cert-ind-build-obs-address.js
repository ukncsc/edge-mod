define([
    "dcl/dcl",
    "cert-ind-build/indicator_builder",
    "cert-ind-build/validation"
], function (declare, indicator_builder, validation) {
    "use strict";

    return declare(indicator_builder.ObservableAddress, {
        constructor: function () {
            this.category.extend({
                validate: {
                    "isValidCallback": validation.hasValue,
                    "failedValidationMessage": "An address category is required."
                }
            });
        },

        doValidation: declare.superCall(function (sup) {
            return function () {
                var msgs = [];
                if (sup) {
                    msgs = sup.call(this);
                }
                if (this.category.hasError()) {
                    msgs.push(this.category.errorMessage());
                }
                return msgs;
            };
        })
    });
});
