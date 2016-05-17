define([
    "dcl/dcl",
    "knockout"
], function (declare, ko) {
    "use strict";

    return declare(null, {
        declaredClass: "Panel",
        constructor: function (/*int*/x, /*int*/y,
                               /*int*/w, /*int*/h,
                               /*string*/label, /*string*/content) {
            this.x = ko.observable(x);
            this.y = ko.observable(y);
            this.w = ko.observable(w);
            this.h = ko.observable(h);
            this.label = ko.observable(label);
            this.content = ko.observable(content);
        }
    });
});
