define([
    "../../dcl/dcl",
    "knockout"
], function (declare, ko) {
    "use strict";

    return declare(null, {
        declaredClass: "PanelAction",
        constructor: function (references/*function*/, referenced_by/*function*/,
                               action/*function*/, action_name/*String*/, glyphicon_name/*String*/) {
            this.references = ko.computed(function () {
                return references;
            });

            this.referenced_by = ko.computed(function () {
                return referenced_by;
            });

            this.action_name = ko.computed(function () {
                return action_name;
            });

            this.glyphicon_name = ko.computed(function () {
                return "glyphicon glyphicon-" + glyphicon_name;
            });

            this.action = ko.computed(function () {
                return action;
            });
        }
    })
});
