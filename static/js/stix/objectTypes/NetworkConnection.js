define([
    "dcl/dcl",
    "knockout",
    "./NamedProperty",
    "./StixObjectType"
], function (declare, ko, NamedProperty, StixObjectType) {
    "use strict";

    return declare(StixObjectType, {
        declaredClass: "NetworkConnection",
        properties: function () {
            var propertyList = [];
            NamedProperty.addToPropertyList(propertyList, "source_socket_address.host", this.stixPackage.safeValueGet(this.id, this.data, "source_socket_address.hostname.hostname_value"));
            NamedProperty.addToPropertyList(propertyList, "source_socket_address.ip", this.stixPackage.safeValueGet(this.id, this.data, "source_socket_address.ip_address.address_value"));
            NamedProperty.addToPropertyList(propertyList, "source_socket_address.port", this.stixPackage.safeValueGet(this.id, this.data, "source_socket_address.port.port_value"));
            NamedProperty.addToPropertyList(propertyList, "source_socket_address.protocol", this.stixPackage.safeValueGet(this.id, this.data, "source_socket_address.port.layer4_protocol"));

            NamedProperty.addToPropertyList(propertyList, "destination_socket_address.host", this.stixPackage.safeValueGet(this.id, this.data, "destination_socket_address.hostname.hostname_value"));
            NamedProperty.addToPropertyList(propertyList, "destination_socket_address.ip", this.stixPackage.safeValueGet(this.id, this.data, "destination_socket_address.ip_address.address_value"));
            NamedProperty.addToPropertyList(propertyList, "destination_socket_address.port", this.stixPackage.safeValueGet(this.id, this.data, "destination_socket_address.port.port_value"));
            NamedProperty.addToPropertyList(propertyList, "destination_socket_address.protocol", this.stixPackage.safeValueGet(this.id, this.data, "destination_socket_address.port.layer4_protocol"));
            return propertyList;
        }
    });
});
