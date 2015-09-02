define([
    "dcl/dcl",
    "knockout",
    "./NamedProperty",
    "./StixObjectType"
], function (declare, ko, NamedProperty, StixObjectType) {
    "use strict";

    return declare(StixObjectType, {
        declaredClass: "WindowsRegistryKey",
        properties: declare.superCall(function (sup) {
            return function () {
                var propertyList = sup.apply(this, arguments);
                var hashes = this.stixPackage.safeGet(this.data, "values");
                if (hashes instanceof Array) {
                    ko.utils.arrayForEach(hashes, function (hash) {
                        NamedProperty.addToPropertyList(
                            propertyList,
                            this.stixPackage.safeGet(hash, "name"),
                            this.stixPackage.safeGet(hash, "data")
                        );
                    }.bind(this));
                }
                return propertyList;
            };
        })
    });
});
