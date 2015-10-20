define([
    "dcl/dcl",
    "cert-ind-build/indicator_builder",
    "cert-ind-build/validation"
], function (declare, indicator_builder, validation) {
    "use strict";

    return declare(indicator_builder.ObservableArtifact, {
        constructor: function () {
            this.artifactType.extend({
                validate: {
                    "isValidCallback": validation.hasValue,
                    "failedValidationMessage": "A artifact type is required."
                }
            });

            this.artifactRaw.extend({
                validate: {
                    "isValidCallback": validation.isNotEmpty,
                    "failedValidationMessage": "Raw data value is required."
                }
            }).valueHasMutated();
        },

        doValidation: declare.superCall(function (sup) {
            return function () {
                var msgs = [];
                if (sup) {
                    msgs = sup.call(this);
                }
                if (this.artifactType.hasError()) {
                    msgs.push(this.artifactType.errorMessage());
                }
                if (this.artifactRaw.hasError()) {
                    msgs.push(this.artifactRaw.errorMessage());
                }
                return msgs;
            };
        })
    });
});
