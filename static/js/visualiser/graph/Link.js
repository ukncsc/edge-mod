define([
    "dcl/dcl",
    "knockout"
], function (declare, ko) {
    "use strict";

    return declare(null, {
        declaredClass: "Link",
        constructor: function (/*Node*/ sourceNode, /*Node*/ targetNode) {
            this.source = sourceNode;
            this.target = targetNode;
            this.isRelated = ko.observable(false);
            this.className = ko.computed(function () {
                return this.isRelated() ? "ko-d3-graph-link related" : "ko-d3-graph-link";
            }, this);
        }
    });
});
