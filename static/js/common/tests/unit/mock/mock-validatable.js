define([
    "../../../../dcl/dcl",
    "knockout"
], function (declare, ko) {
    "use strict";

    return declare(null, {
        declaredClass: "MockValidatable",
        constructor: function (hasError, errorString) {
            this.hasError = ko.observable(hasError);
            this.displayErrorMessage = ko.observable(errorString);
        }
    });
});
