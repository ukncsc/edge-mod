define([
    "dcl/dcl",
    "cert-ind-build/indicator_builder",
    "cert-ind-build/validation"
], function (declare, indicator_builder, validation) {
    "use strict";

    return declare(indicator_builder.ObservableEmail, {
        constructor: function () {
            this.from.extend({
                validate: {
                    "isValidCallback": validation.isNotEmpty,
                    "failedValidationMessage": "The 'from' field must be populated."
                }
            }).valueHasMutated();

            this.subject.extend({
                validate: {
                    "isValidCallback": validation.isNotEmpty,
                    "failedValidationMessage": "The subject is required."
                }
            }).valueHasMutated();
        },

        doValidation: declare.superCall(function (sup) {
            return function () {
                var msgs = [];
                if (sup) {
                    msgs = sup.call(this);
                }
                if (this.from.hasError()) {
                    msgs.push(this.from.errorMessage());
                }
                if (this.subject.hasError()) {
                    msgs.push(this.subject.errorMessage());
                }
                return msgs;
            };
        })
    });
});
