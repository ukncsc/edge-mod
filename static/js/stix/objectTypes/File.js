define([
    "dcl/dcl",
    "knockout",
    "./NamedProperty",
    "./StixObjectType"
], function (declare, ko, NamedProperty, StixObjectType) {
    "use strict";

    return declare(StixObjectType, {
        declaredClass: "File",
        properties: declare.superCall(function (sup) {
            return function () {
                var propertyList = sup.apply(this, arguments);
                NamedProperty.removeFromPropertyList(propertyList, "hashes");
                var hashes = this.stixPackage.safeGet(this.data, "hashes");
                if (hashes instanceof Array) {
                    ko.utils.arrayForEach(hashes, function (hash) {
                        NamedProperty.addToPropertyList(
                            propertyList,
                            this.stixPackage.safeValueGet(this.id, hash, "type").value(),
                            this.stixPackage.safeValueGet(this.id, hash, "simple_hash_value")
                        );
                    }.bind(this));
                }
                return propertyList;
            };
        })
    });
});
