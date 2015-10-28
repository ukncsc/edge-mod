define([
    "dcl/dcl",
    "knockout",
    "./NamedProperty"
], function (declare, ko, NamedProperty) {
    "use strict";

    return declare(null, {
        declaredClass: "StixObjectType",
        constructor: function (data, stixPackage, cert_validation) {
            this.data = data;
            this.stixPackage = stixPackage;
            this.cert_validation = cert_validation;
        },
        properties: function () {
            var propertyList = [];
            ko.utils.objectForEach(this.data, function (name, value) {
                if (name === "xsi:type") {
                    return;
                }
                var validationInfo = this.cert_validation[name];
                NamedProperty.addToPropertyList(propertyList, name, value, validationInfo);
            }.bind(this));
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
