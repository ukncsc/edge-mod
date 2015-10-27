define([
    "dcl/dcl",
    "cert-ind-build/indicator-builder-shim",
    "cert-ind-build/validation"
], function (declare, indicator_builder, validation) {
    "use strict";

    var CERTObservableArtifact = declare(indicator_builder.ObservableArtifact, {
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
                var msgs = sup.call(this);
                if (this.artifactType.hasError()) {
                    msgs.addError(this.artifactType.errorMessage());
                }
                if (this.artifactRaw.hasError()) {
                    msgs.addError(this.artifactRaw.errorMessage());
                }
                return msgs;
            };
        })
    });
    indicator_builder.ObservableArtifact = CERTObservableArtifact;
    return CERTObservableArtifact
});
