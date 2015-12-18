define([
    "dcl/dcl",
    "knockout",
    "kotemplate!duplicates-view:./templates/duplicates-view.html"
], function (declare, ko) {
    "use strict";

    return declare(null, {
        declaredClass: "DuplicateModel",
        constructor: function (duplicates) {
            this.duplicates = ko.observable(duplicates);
        }
    });
});
