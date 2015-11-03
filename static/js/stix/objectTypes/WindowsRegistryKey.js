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
                NamedProperty.removeFromPropertyList(propertyList, "values");
                var values = this.stixPackage.safeGet(this.data, "values");
                if (values instanceof Array) {
                    ko.utils.arrayForEach(values, function (value) {
                        NamedProperty.addToPropertyList(
                            propertyList,
                            this.stixPackage.safeGet(value, "name"),
                            this.stixPackage.safeValueGet(this.id, value, "data")
                        );
                    }.bind(this));
                }
                return propertyList;
            };
        })
    });
});
