define([
    "dcl/dcl",
    "knockout",
    "cert-ind-build/indicator-builder-shim"
], function (declare, ko, indicator_builder) {
    "use strict";

    var CERTGeneral = declare(indicator_builder.General, {
        constructor: function () {
            this.indicatorType.extend({ required: true });
            this.tlp.extend({ required: true });
            this.killChainPhase = ko.observable("").extend({ required: true });

            this.kill_chain_phase_list = ko.observableArray([]);
        },

        loadStatic: declare.superCall(function (sup) {
            return function (optionLists) {
                sup.call(this, optionLists);
                this.kill_chain_phase_list(optionLists['kill_chain_phase_list']);
            }
        }),

        doValidation: declare.superCall(function (sup) {
            return function () {
                var msgs = sup.call(this);
                if (!this.indicatorType()) {
                    msgs.addError("You need to select a type for your indicator");
                }
                if (!this.tlp()) {
                    msgs.addError("You need to select a TLP for your indicator");
                }
                if (!this.killChainPhase()) {
                    msgs.addError("You need to select a kill chain phase for your indicator");
                }
                return msgs;
            }
        }),

        load: declare.superCall(function (sup) {
            return function (data) {
                sup.call(this, data);
                this.killChainPhase(data["kill_chain_phase"] || "");
            }
        }),

        save: declare.superCall(function (sup) {
            return function () {
                var baseData = sup.call(this);
                baseData['kill_chain_phase'] = this.killChainPhase();
                return baseData;
            }
        })
    });

    indicator_builder.General = CERTGeneral;
    return CERTGeneral;
});
