define([
    "dcl/dcl",
    "./NamedProperty",
    "./StixObjectType"
], function (declare, NamedProperty, StixObjectType) {
    "use strict";

    return declare(StixObjectType, {
        declaredClass: "EmailMessage",
        properties: function () {
            var propertyList = [];
            NamedProperty.addToPropertyList(propertyList, "from", this.stixPackage.safeGet(this.data, "header.from.address_value"));
            NamedProperty.addToPropertyList(propertyList, "to", this.stixPackage.safeListGet(this.data, "header.to", "address_value"));
            NamedProperty.addToPropertyList(propertyList, "cc", this.stixPackage.safeListGet(this.data, "header.cc", "address_value"));
            NamedProperty.addToPropertyList(propertyList, "bcc", this.stixPackage.safeListGet(this.data, "header.bcc", "address_value"));
            NamedProperty.addToPropertyList(propertyList, "subject", this.stixPackage.safeGet(this.data, "header.subject"));
            NamedProperty.addToPropertyList(propertyList, "date", this.stixPackage.safeGet(this.data, "header.date"));
            NamedProperty.addToPropertyList(propertyList, "raw_body", this.stixPackage.safeGet(this.data, "raw_body"));
            return propertyList;
        }
    });
});
