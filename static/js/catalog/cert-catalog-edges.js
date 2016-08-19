define([
    "dcl/dcl",
    "knockout"
], function (declare, ko) {
    "use strict";

    return declare(null, {
        declaredClass: "CatalogEdges",
        constructor: function () {
            this.label = ko.observable("Edges");
            this.edges = ko.observableArray([]);
        },

        loadStatic: function (optionsList) {
            this.edges(optionsList.edges);
        }
    });
});
