define([
    "dcl/dcl",
    "knockout",
    "ind-build/builder-shim",
    "ind-build/indicator-builder-shim",
    "common/cert-abstract-builder-form",
    "ind-build/cert-ind-build-snort-rule",
    "ind-build/cert-ind-build-yara-rule"
], function (declare, ko, builder, indicator_builder, AbstractBuilderForm, SnortRule, YaraRule) {
    "use strict";

    var TestMechanisms = declare(AbstractBuilderForm, {
        declaredClass: "TestMechanisms",

        constructor: declare.superCall(function (sup) {
            return function () {
                this.snortRules = ko.observableArray([]);
                this.yaraRules = ko.observableArray([]);
                this.rules = ko.computed(function() {
                    return this.snortRules().concat(this.yaraRules());
                }, this)

                sup.call(this, "Test Mechanisms");
            }
        }),

        addSnortRule: function () {
            var new_rule = new SnortRule();
            this.snortRules.push(new_rule)
        },

        addYaraRule: function () {
            var new_rule = new YaraRule();
            this.yaraRules.push(new_rule);
        },

        removeSnortRule: function (rule) {
            this.snortRules.remove(rule);
        },

        removeYaraRule: function (rule) {
            this.yaraRules.remove(rule);
        },

        load: function (data) {
            this.snortRules.removeAll();
            this.yaraRules.removeAll();
            var self = this;
            if ('test_mechanisms' in data) {
                $.each(data['test_mechanisms'], function (i, v) {
                    if(v['type'] == 'Snort') {
                        var new_snort_id = new SnortRule();
                        new_snort_id.load(v['rules']);
                        self.snortRules.push(new_snort_id);
                    }
                    else if(v['type'] == 'Yara') {
                        var new_yara_id = new YaraRule();
                        new_yara_id.load(v['rule']);
                        self.yaraRules.push(new_yara_id);
                    }
                });
            }
        },

        save: function () {
            var data = {};
            data['test_mechanisms'] = [];
            ko.utils.arrayForEach(this.rules(), function (rule) {
                data['test_mechanisms'].push(rule.to_json());
            });

            return data;
        },

        counter: function () {
            return this.rules().length || "";
        }

    });
    indicator_builder.TestMechanisms = TestMechanisms;
    return TestMechanisms;
});
