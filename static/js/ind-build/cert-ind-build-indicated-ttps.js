define([
    "dcl/dcl",
    "ind-build/builder-shim",
    "ind-build/indicator-builder-shim"
], function (declare, builder, indicator_builder) {
    "use strict";

    var CERTIndicatedTTPs = declare(indicator_builder.IndicatedTTPs, {
        declaredClass: "CERTIndicatedTTPs",
        doValidation: declare.superCall(function (sup) {
            return function () {
                var msgs = sup.call(this) || new builder.Messages();
                if (this.relatedItems().length < 1) {
                    msgs.addError("Needs at least one Indicated TTP")
                }
                return msgs;
            }
        })
    });
    indicator_builder.IndicatedTTPs = CERTIndicatedTTPs;
    return CERTIndicatedTTPs;
});
