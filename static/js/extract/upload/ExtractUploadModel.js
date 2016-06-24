define([
    "dcl/dcl",
    "knockout"
], function (declare,ko) {
    "use strict";

    return declare(null, {
        declaredClass: "ExtractUploadModel",
        constructor: function () {
            this.results = ko.observableArray([]);
            this.exists = ko.observable(false);
            this.fileName = ko.observable("");
        },
        onFileSelected: function (data, event) {
            this.fileName(event.target.files[0].name);
            this.exists(true);
        },
        submitted: function(data, event) {
            this.exists(false);
            this.fileName("");
            return true;
        }
    });
});
