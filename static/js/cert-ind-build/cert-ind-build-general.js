define([
    "dcl/dcl",
    "cert-ind-build/indicator-builder-shim",
    "cert-ind-build/validation"
], function (declare, indicator_builder, validation) {
    "use strict";

    var CERTGeneral = declare(indicator_builder.General, {
        constructor: function () {
            this.indicatorType.extend({ required: true });
            this.tlp.extend({ required: true });
        },

        doValidation: declare.superCall(function (sup) {
            return function () {
                var msgs = sup.call(this);
                if (!this.indicatorType()) {
                    msgs.addError("You need to select a type for your indicator");
                }
                if (!this.tlp()) {
                    msgs.addError("You need to select a TLP for your indicator");
                }
                return msgs;
            }
        })
    });

    // replace the 'General' tab model with an instance of CERTGeneral with the same data
    var original = indicator_builder.vm.section().findByLabel("General")();
    var certGeneral = new CERTGeneral();
    certGeneral.loadStatic({
        indicatorTypes: original.indicator_type_list(),
        confidence_list: original.confidences(),
        tlps_list: original.tlps()
    });
    certGeneral.load({
        title: original.title(),
        indicatorType: original.indicatorType(),
        short_description: original.short_description(),
        description: original.description(),
        confidence: original.confidence(),
        tlp: original.tlp(),
        producer: original.producer(),
        markings: original.markings()
    });
    indicator_builder.vm.section().findByLabel("General")(certGeneral);

    indicator_builder.General = CERTGeneral;
    return CERTGeneral;
});
