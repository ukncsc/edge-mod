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
            (new NamedProperty("from", this.stixPackage.safeGet(this.data, "header.from.address_value"))).addToPropertyList(propertyList);
            (new NamedProperty("to", this.stixPackage.safeListGet(this.data, "header.to", "address_value"))).addToPropertyList(propertyList);
            (new NamedProperty("cc", this.stixPackage.safeListGet(this.data, "header.cc", "address_value"))).addToPropertyList(propertyList);
            (new NamedProperty("bcc", this.stixPackage.safeListGet(this.data, "header.bcc", "address_value"))).addToPropertyList(propertyList);
            (new NamedProperty("subject", this.stixPackage.safeGet(this.data, "header.subject"))).addToPropertyList(propertyList);
            (new NamedProperty("date", this.stixPackage.safeGet(this.data, "header.date"))).addToPropertyList(propertyList);
            (new NamedProperty("raw body", this.stixPackage.safeGet(this.data, "raw_body"))).addToPropertyList(propertyList);
            return propertyList;
        }
    });
});
