define([
    "dcl/dcl",
    "knockout"
], function (declare, ko) {
    "use strict";

    return declare(null, {
        declaredClass: "References",
        constructor: function () {
            this.label = ko.observable("References");
            this.backEdges = ko.observableArray([]);
        },

        loadStatic: function (optionsList) {
            this.backLinks(optionsList.backLinks);
        }
    });
});
