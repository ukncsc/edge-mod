define([
    "dcl/dcl",
    "knockout"
], function (declare, ko) {
    "use strict";

    return declare(null, {
        declaredClass: "cert-ind-build-detection-rule",
        constructor: function () {
            this.type = ko.observable('');
            this.rules = ko.observableArray([]);
        },

        addRule: function () {
            this.rules.push(ko.observable({
                rule: ''
            }));
        },

        removeRule: function (index, data) {
            this.rules.splice(index, 1)
        }
    });
});
