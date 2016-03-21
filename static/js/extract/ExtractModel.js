define([
    "dcl/dcl",
    "knockout"
], function (declare,ko) {
    "use strict";

    return declare(null, {
        declaredClass: "ExtractModel",
        constructor: function () {
            this.results = ko.observableArray([]);
            this.exists = ko.observable(false);
            this.fileName = ko.observable("");
        },
        onFileSelected: function (data, event) {
            this.fileName(event.target.files[0].name);
            this.exists(true);
        }
    });
});
