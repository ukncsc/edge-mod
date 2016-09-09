define([
    "dcl/dcl",
    "knockout",
    "ind-build/indicator-builder-shim",
    "common/cert-messages"
], function (declare, ko, indicator_builder, Messages) {
    "use strict";

    var Section = declare(indicator_builder.Section, {
        declaredClass: "cert-ind-build-section",

        constructor: declare.superCall(function (sup) {
            return function () {
                sup.call(this);

                function indexBy(items, pname) {
                    var indexed = {};
                    ko.utils.arrayForEach(items(), function (item) {
                        indexed[item()[pname]()] = item;
                    });
                    return indexed;
                };


                this.options = ko.observableArray([
                    ko.observable(new indicator_builder.General()),
                    ko.observable(new indicator_builder.TrustGroups()),
                    ko.observable(new indicator_builder.Observables()),
                    ko.observable(new indicator_builder.IndicatedTTPs()),
                    ko.observable(new indicator_builder.RelatedIndicators()),
                    ko.observable(new indicator_builder.SuggestedCOAs()),
                    ko.observable(new indicator_builder.TestMechanisms())
                ]);
                this._byLabel = indexBy(this.options, "label");
                this.value = ko.observable(
                    this.options()[0]()
                );
            }
        }),
        doValidation: function () {
            var msgs = new Messages();
            ko.utils.arrayForEach(this.options(), function (option) {
                var optionMsgs = option().doValidation();
                if (optionMsgs !== null && optionMsgs.hasMessages()) {
                    msgs.addMessages(optionMsgs);
                }
            });
            return msgs;
        },
    });
    indicator_builder.Section = Section;
    return Section;
});
