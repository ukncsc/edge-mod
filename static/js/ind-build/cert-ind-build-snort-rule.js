define([
    "dcl/dcl",
    "knockout"
], function (declare, ko) {
    "use strict";

    return declare(null, {
        declaredClass: "SnortTestMechanism",
        constructor: function () {
            this.rules = ko.observableArray([]);
        },

        addRule: function () {
            var rule = ko.observable('');
            this.rules.push(rule);
        },

        removeRule: function (index, data) {
            this.rules.splice(index, 1)
        },

        load: function (rules) {
            var extractedRules = [];
            ko.utils.arrayForEach(rules, function (item) {
                extractedRules.push(ko.observable(item.value))
            });
            this.rules(extractedRules);
        },

        to_json: function () {
            var extractedRules = [];
            ko.utils.arrayForEach(this.rules(), function (item) {
                extractedRules.push({
                    value: item()
                });
            });
            return {
                type: 'Snort',
                rules: extractedRules
            }
        }

    });
});
