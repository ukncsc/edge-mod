define([
    "dcl/dcl",
    "knockout"
], function (declare, ko) {
    "use strict";

    return declare(null, {
        declaredClass: "cert-ind-build-detection-rule",
        constructor: function () {
            this.rule = ko.observable('');
            this.description = ko.observable('');
            this.producer = ko.observable('')
        }
    });
});
