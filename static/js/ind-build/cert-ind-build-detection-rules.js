define([
    "dcl/dcl",
    "knockout",
    "ind-build/builder-shim",
    "ind-build/indicator-builder-shim",
    "common/cert-abstract-builder-form",
    "ind-build/cert-ind-build-detection-rule"
], function (declare, ko, builder, indicator_builder, AbstractBuilderForm, DetectionRule) {
    "use strict";

    var DetectionRules = declare(AbstractBuilderForm, {
        declaredClass: "DetectionRules",

        constructor: declare.superCall(function (sup) {
            return function () {
                sup.call(this, "Detection Rules");

                this.rules = ko.observableArray([]);
                this.options = ko.observableArray(['Snort', 'Yara'])
            }
        }),

        add: function () {
            var new_rule = new DetectionRule();
            this.rules.push(new_rule);
        },

        remove: function (rule) {
            this.rules.remove(rule);
        }

    });
    indicator_builder.DetectionRules = DetectionRules;
    return DetectionRules;
});
