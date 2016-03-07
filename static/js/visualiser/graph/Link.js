define([
    "dcl/dcl",
    "knockout"
], function (declare, ko) {
    "use strict";

    return declare(null, {
        declaredClass: "Link",
        constructor: function (linkData) {
            this.source = 0 + linkData.source;
            this.target = 0 + linkData.target;
        }
    });
});
