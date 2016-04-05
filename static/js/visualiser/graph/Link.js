define([
    "dcl/dcl"
], function (declare) {
    "use strict";

    return declare(null, {
        declaredClass: "Link",
        constructor: function (/*Node*/ sourceNode, /*Node*/ targetNode) {
            this.source = sourceNode;
            this.target = targetNode;
        }
    });
});
