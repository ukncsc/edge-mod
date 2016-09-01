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
                this.rules = ko.computed(function () {
                    return this.snortRules().concat(this.yaraRules());
                }, this);

                sup.call(this, "Test Mechanisms");
            }
        }),

        addSnortRule: function () {
            var new_rule = new SnortRule();
            this.addSnortRuleValidation(new_rule);
            this.snortRules.push(new_rule);
        },

        addYaraRule: function () {
            var new_rule = new YaraRule();
            this.addYaraRuleValidation(new_rule);
            this.yaraRules.push(new_rule);
        },

        removeSnortRule: function (rule) {
            ko.utils.objectForEach(rule, function (name, key) {
                ko.utils.arrayForEach(key(), function (rule) {
                    this.validationGroup.remove(rule)
                }.bind(this))
            }.bind(this));
            this.snortRules.remove(rule);
        },

        removeYaraRule: function (rule) {
            this.validationGroup.remove(rule.rule);
            this.yaraRules.remove(rule);
        },

        addYaraRuleValidation: function (new_rule) {
            new_rule.rule.extend({
                requiredGrouped: {
                    required: true,
                    group: this.validationGroup,
                    displayMessage: "You need to enter a value for your Yara rule"
                }
            });
        },

        addSnortRuleValidation: function (new_rule) {
           new_rule.rules.subscribe(function () {
                ko.utils.arrayForEach(new_rule.rules(), function (rule) {
                    rule.extend({
                        requiredGrouped: {
                            required: true,
                            group: this.validationGroup,
                            displayMessage: "You need to enter a value for your Snort rule"
                        }
                    });
                }.bind(this))
            }.bind(this));

            new_rule.rules.subscribe(function () {
                ko.utils.arrayForEach(new_rule.rules(), function (rule) {
                    this.validationGroup.remove(rule);
                }.bind(this))
            }.bind(this), null, "beforeChange");
        },

        load: function (data) {
            this.snortRules.removeAll();
            this.yaraRules.removeAll();
            var self = this;
            if ('test_mechanisms' in data) {
                $.each(data['test_mechanisms'], function (i, v) {
                    if (v['type'] == 'Snort') {
                        var new_id = new SnortRule();
                        self.addSnortRuleValidation(new_id);
                        new_id.load(v['rules']);
                        self.snortRules.push(new_id);
                    }
                    else if (v['type'] == 'Yara') {
                        var new_id = new YaraRule();
                        self.addYaraRuleValidation(new_id)
                        new_id.load(v['rule']);
                        self.yaraRules.push(new_id);
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
