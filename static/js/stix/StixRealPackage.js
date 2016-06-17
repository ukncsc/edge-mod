define([
    "dcl/dcl",
    "knockout",
    "./StixObject",
    "kotemplate!flat-stix:./templates/flat-Package.html",
], function (declare, ko, StixObject) {
    "use strict";

    return declare(StixObject, {
        constructor: function (data, stixPackage) {
            this.title = ko.computed(function () {
                return stixPackage.safeValueGet(this.id(), this.data(), "stix_header.title");
            }, this);
        }
    });
});
