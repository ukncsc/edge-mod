define([
    "dcl/dcl",
    "ind-build/indicator-builder-shim",
    "ind-build/validation"
], function (declare, indicator_builder, validation) {
    "use strict";

    var CERTObservableAddress = declare(indicator_builder.ObservableAddress, {
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
                var msgs = sup.call(this);
                if (this.category.hasError()) {
                    msgs.addError(this.category.errorMessage());
                }
                return msgs;
            };
        })
    });
    indicator_builder.ObservableAddress = CERTObservableAddress;
    return CERTObservableAddress;
});
