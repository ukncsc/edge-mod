define([
    "../../dcl/dcl",
    "knockout"
], function (declare, ko) {
    "use strict";

    return declare(null, {
        declaredClass: "PanelAction",
        constructor: function (applies_to_link/*function*/,
                               action/*function*/, action_name/*String*/, glyphicon_name/*String*/) {
            this.applies_to_link = ko.computed(function () {
                return applies_to_link;
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
