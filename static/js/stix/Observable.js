define([
    "dcl/dcl",
    "knockout",
    "./StixObject",
    "./objectTypes/StixObjectType",
    "./objectTypes/Address",
    "./objectTypes/DomainName",
    "./objectTypes/EmailMessage",
    "./objectTypes/File",
    "./objectTypes/Mutex",
    "./objectTypes/URI",
    "kotemplate!root-obs:./templates/root-Observable.html",
    "kotemplate!observables:./templates/Observables.html",
    "kotemplate!related-observables:./templates/related-Observables.html"
], function (declare, ko, StixObject, StixObjectType, AddressObjectType, DomainNameObjectType, EmailMessageObjectType,
             FileObjectType, MutexObjectType, URIObjectType) {
    "use strict";

    var OBJECT_TYPES = Object.freeze({
        "AddressObjectType": AddressObjectType,
        "DomainNameObjectType": DomainNameObjectType,
        "EmailMessageObjectType": EmailMessageObjectType,
        "FileObjectType": FileObjectType,
        "MutexObjectType": MutexObjectType,
        "URIObjectType": URIObjectType
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
