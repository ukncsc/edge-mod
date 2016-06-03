define([
        "dcl/dcl",
        "knockout",
        "./StixObject",
        "./objectTypes/StixObjectType",
        "./objectTypes/EmailMessage",
        "./objectTypes/File",
        "./objectTypes/HttpSession",
        "./objectTypes/NetworkConnection",
        "./objectTypes/SocketAddress",
        "./objectTypes/WindowsRegistryKey",
        "kotemplate!root-obs:./templates/root-Observable.html",
        "kotemplate!flat-obs:./templates/flat-Observable.html",
        "kotemplate!list-obs:./templates/list-Observables.html"
    ], function (declare, ko, StixObject, StixObjectType, EmailMessageObjectType, FileObjectType, HTTPSessionObjectType, NetworkConnectionObjectType,
                 SocketAddressObjectType, WindowsRegistryKeyObjectType) {
        "use strict";

        var OBJECT_TYPES = Object.freeze({
            "EmailMessageObjectType": EmailMessageObjectType,
            "FileObjectType": FileObjectType,
            "HTTPSessionObjectType": HTTPSessionObjectType,
            "SocketAddressObjectType": SocketAddressObjectType,
            "WindowsRegistryKeyObjectType": WindowsRegistryKeyObjectType,
            "NetworkConnectionObjectType": NetworkConnectionObjectType
        });

        function getObjectType(type) {
            return OBJECT_TYPES[type] || StixObjectType;
        }

        return declare(StixObject, {
            constructor: function (data, stixPackage) {
                this.type = ko.computed(function () {
                    var type = stixPackage.safeValueGet(this.id(), this.data(), "object.properties.xsi:type", "xsi:type");
                    return type.isEmpty() === false ? type : stixPackage.safeValueGet(this.id(), this.data(), "observable_composition.operator");
                }, this);
                var objectType = ko.computed(function () {
                    var type = stixPackage.safeGet(this.data(), "object.properties.xsi:type");
                    var ctor = getObjectType(type);
                    return new ctor(this.id(), stixPackage.safeGet(this.data(), "object.properties"), stixPackage);
                }, this);
                this.properties = ko.computed(function () {
                    return objectType().properties();
                }, this);
            }
        });
    }
)
;
