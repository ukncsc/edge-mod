define([
    "dcl/dcl",
    "knockout"
], function (declare, ko) {
    "use strict";

    return declare(null, {
        declaredClass: "Node",
        constructor: function (nodeData) {
            this.id = ko.observable(nodeData.id);
            this.type = ko.observable(nodeData.type);
            this.title = ko.observable(nodeData.title);
            this.depth = ko.observable(nodeData.depth);
            this.d3data = ko.observable({});
        },
        isRoot: function() {
            return this.depth === 0;
        }
    });
});
