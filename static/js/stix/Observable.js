define([
    "dcl/dcl",
    "knockout",
    "./StixObject",
    "./objectTypes/StixObjectType",
    "./objectTypes/EmailMessage",
    "./objectTypes/File",
    "./objectTypes/WindowsRegistryKey",
    "kotemplate!root-obs:./templates/root-Observable.html",
    "kotemplate!list-obs:./templates/list-Observables.html"
], function (declare, ko, StixObject, StixObjectType, EmailMessageObjectType,
             FileObjectType, WindowsRegistryKeyObjectType) {
    "use strict";

    var OBJECT_TYPES = Object.freeze({
        "EmailMessageObjectType": EmailMessageObjectType,
        "FileObjectType": FileObjectType,
        "WindowsRegistryKeyObjectType": WindowsRegistryKeyObjectType
    });

    function getObjectType(type) {
        return OBJECT_TYPES[type] || StixObjectType;
    }

    return declare(StixObject, {
        constructor: function (data, stixPackage) {
            this.type = ko.computed(function () {
                return stixPackage.safeGet(this.data(), "object.properties.xsi:type");
            }, this);
            var objectType = ko.computed(function () {
                var ctor = getObjectType(this.type());
                return new ctor(stixPackage.safeGet(this.data(), "object.properties"), stixPackage);
            }, this);
            this.properties = ko.computed(function () {
                return objectType().properties();
            }, this);
        }
    });
});
