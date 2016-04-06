define([
    "dcl/dcl",
    "knockout"
], function (declare, ko, d3, Graph, StixPackage) {
    "use strict";

    return declare(null, {
        declaredClass: "PanelActions",
        constructor: function (references, referenced_by, action, action_name) {
            this.references = ko.computed(function () {
                return references;
            });

            this.referenced_by = ko.computed(function () {
                return referenced_by;
            });

            this.action_name = ko.computed(function () {
                return action_name;
            });

            this.action = ko.computed(function () {
                return action;
            });
        }
    })
});
