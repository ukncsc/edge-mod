define([
    "dcl/dcl",
    "knockout"
], function (declare, ko) {
    "use strict";

    return declare(null, {
        declaredClass: "SnortTestMechanism",
        constructor: function () {
            this.rules = ko.observableArray([ko.observable({
                value: ''
            })]);

        },

        addRule: function () {
            this.rules.push(ko.observable({
                value: ''
            }));
        },

        removeRule: function (index, data) {
            this.rules.splice(index, 1)
        },

       load: function(rules) {
            var extractedRules = [];
            ko.utils.arrayForEach(rules, function (item) {
                extractedRules.push(ko.observable({
                    value: item.value
                }))
            });
            this.rules(extractedRules);
        },

        to_json: function() {
            var extractedRules = [];
            ko.utils.arrayForEach(this.rules(), function (item) {
                extractedRules.push({
                    value: item().value
                });
            });
            return {
                type: 'Snort',
                rules: extractedRules
            }
        }

    });
});
