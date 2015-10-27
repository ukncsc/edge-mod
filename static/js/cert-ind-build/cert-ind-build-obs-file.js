define([
    "dcl/dcl",
    "cert-ind-build/indicator-builder-shim",
    "cert-ind-build/validation"
], function (declare, indicator_builder, validation) {
    "use strict";

    var CERTObservableFile = declare(indicator_builder.ObservableFile, {
        constructor: function () {
            this.file_name.extend({
                validate: {
                    "isValidCallback": validation.isNotEmpty,
                    "failedValidationMessage": "A file name is required."
                }
            }).valueHasMutated();
        },

        doValidation: declare.superCall(function (sup) {
            return function () {
                var msgs = sup.call(this);
                if (this.file_name.hasError()) {
                    msgs.addError(this.file_name.errorMessage());
                }
                return msgs;
            };
        })
    });
    indicator_builder.ObservableFile = CERTObservableFile;
    return CERTObservableFile;
});
