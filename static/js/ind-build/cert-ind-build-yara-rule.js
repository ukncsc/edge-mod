define([
    "dcl/dcl",
    "knockout"
], function (declare, ko) {
    "use strict";

    return declare(null, {
        declaredClass: "YaraTestMechanism",
        constructor: function () {
            this.rule = ko.observable('');
        },

        load: function (rule) {
            this.rule(rule.value);
        },

        to_json: function () {
            return {
                type: 'Yara',
                rule: {
                    value: this.rule()
                }
            }
        }
    });
});
