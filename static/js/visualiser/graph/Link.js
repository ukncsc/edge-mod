define([
    "dcl/dcl",
    "knockout"
], function (declare, ko) {
    "use strict";

    return declare(null, {
        declaredClass: "Link",
        constructor: function (/*Node*/ sourceNode, /*Node*/ targetNode, /*String*/ rel_type) {
            this.source = sourceNode;
            this.target = targetNode;
            this.isRelated = ko.observable(false);
            this.relType = ko.observable(rel_type);
            this.className = ko.computed(function () {
                return this.isRelated() ? "ko-d3-graph-link related " + this.relType() : "ko-d3-graph-link " + this.relType();
            }, this);
        }
    });
});
