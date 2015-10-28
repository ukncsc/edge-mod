define([
    "dcl/dcl",
    "knockout",
    "./NamedProperty"
], function (declare, ko, NamedProperty) {
    "use strict";

    return declare(null, {
        declaredClass: "StixObjectType",
        constructor: function (data, stixPackage) {
            this.data = data;
            this.stixPackage = stixPackage;
        },
        properties: function () {
            var propertyList = [];
            ko.utils.objectForEach(this.data, function (name, value) {
                if (name === "xsi:type") {
                    return;
                }
                NamedProperty.addToPropertyList(propertyList, name, value);
            });
            var customProperties = this.stixPackage.safeGet(this.data, "custom_properties");
            if (customProperties instanceof Array) {
                ko.utils.arrayForEach(customProperties, function (property) {
                    if (property.name === "xsi:type") {
                        return;
                    }
                    NamedProperty.addToPropertyList(propertyList, property.name, property.value);
                });
            }
            return propertyList;
        }
    });
});
