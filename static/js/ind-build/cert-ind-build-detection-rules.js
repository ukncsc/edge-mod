define([
    "dcl/dcl",
    "ind-build/builder-shim",
    "ind-build/indicator-builder-shim",
    "common/cert-abstract-builder-form",
    "ind-build/cert-ind-build-detection-rule"
], function (declare, builder, indicator_builder, AbstractBuilderForm, DetectionRule) {
    "use strict";

    var DetectionRules = declare(AbstractBuilderForm, {
        declaredClass: "DetectionRules",

        constructor: declare.superCall(function (sup) {
            return function () {
                this.rules = ko.observableArray([]);
                sup.call(this, "Detection Rules");

                this.options = ko.observableArray(['Snort', 'Yara'])
            }
        }),

        add: function() {
            var new_rule = new DetectionRule();
            this.rules.push(new_rule);
        }

    });
    indicator_builder.DetectionRules = DetectionRules;
    return DetectionRules;
});
