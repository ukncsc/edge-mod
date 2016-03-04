define([
    "dcl/dcl",
    "knockout"
], function (declare, ko) {
    "use strict";

    return declare(null, {
        declaredClass: "Link",
        constructor: function (linkData) {
            this.source = ko.observable(linkData.source);
            this.target = ko.observable(linkData.target);
            this.d3data = ko.observable({});
        }
    });
});
