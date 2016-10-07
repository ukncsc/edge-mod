define([
    "dcl/dcl",
    "./NamedProperty",
    "./StixObjectType"
], function (declare, NamedProperty, StixObjectType) {
    "use strict";

    return declare(StixObjectType, {
        declaredClass: "Port",
        properties: function () {
            var propertyList = [];
            NamedProperty.addToPropertyList(propertyList, "port_value", this.stixPackage.safeValueGet(this.id, this.data, "port_value"));
            NamedProperty.addToPropertyList(propertyList, "layer4_protocol", this.stixPackage.safeValueGet(this.id, this.data, "layer4_protocol"));
            return propertyList;
        }
    });
});
