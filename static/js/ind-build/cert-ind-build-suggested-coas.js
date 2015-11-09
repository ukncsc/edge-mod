define([
    "dcl/dcl",
    "ind-build/builder-shim",
    "ind-build/indicator-builder-shim"
], function (declare, builder, indicator_builder) {
    "use strict";

    var CERTSuggestedCOAs = declare(indicator_builder.SuggestedCOAs, {
        declaredClass: "CERTSuggestedCOAs",
        doValidation: declare.superCall(function (sup) {
            return function () {
                var msgs = sup.call(this) || new builder.Messages();
                if (this.relatedItems().length < 1) {
                    msgs.addError("Needs at least one Suggested COA")
                }
                return msgs;
            }
        })
    });
    indicator_builder.SuggestedCOAs = CERTSuggestedCOAs;
    return CERTSuggestedCOAs;
});
