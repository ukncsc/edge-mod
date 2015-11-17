define([
    "dcl/dcl",
    "knockout",
    "./NamedProperty",
    "./StixObjectType"
], function (declare, ko, NamedProperty, StixObjectType) {
    "use strict";

    return declare(StixObjectType, {
        declaredClass: "SocketAddress",
        properties: function () {
            var propertyList = [];
            NamedProperty.addToPropertyList(propertyList, "hostname", this.stixPackage.safeValueGet(this.id, this.data, "hostname.hostname_value"));
            NamedProperty.addToPropertyList(propertyList, "ip_address", this.stixPackage.safeValueGet(this.id, this.data, "ip_address.address_value"));
            NamedProperty.addToPropertyList(propertyList, "port", this.stixPackage.safeValueGet(this.id, this.data, "port.port_value"));
            NamedProperty.addToPropertyList(propertyList, "protocol", this.stixPackage.safeValueGet(this.id, this.data, "port.layer4_protocol"));
            return propertyList;
        }
    });
});
