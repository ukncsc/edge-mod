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
            NamedProperty.addToPropertyList(propertyList, "src_host", this.stixPackage.safeValueGet(this.id, this.data, "source_socket_address.hostname.hostname_value"));
            NamedProperty.addToPropertyList(propertyList, "src_IP", this.stixPackage.safeValueGet(this.id, this.data, "source_socket_address.ip_address.address_value"));
            NamedProperty.addToPropertyList(propertyList, "src_port", this.stixPackage.safeValueGet(this.id, this.data, "source_socket_address.port.port_value"));
            NamedProperty.addToPropertyList(propertyList, "src_protocol", this.stixPackage.safeValueGet(this.id, this.data, "source_socket_address.port.layer4_protocol"));

            NamedProperty.addToPropertyList(propertyList, "dst_host", this.stixPackage.safeValueGet(this.id, this.data, "destination_socket_address.hostname.hostname_value"));
            NamedProperty.addToPropertyList(propertyList, "dst_IP", this.stixPackage.safeValueGet(this.id, this.data, "destination_socket_address.ip_address.address_value"));
            NamedProperty.addToPropertyList(propertyList, "dst_port", this.stixPackage.safeValueGet(this.id, this.data, "destination_socket_address.port.port_value"));
            NamedProperty.addToPropertyList(propertyList, "dst_protocol", this.stixPackage.safeValueGet(this.id, this.data, "destination_socket_address.port.layer4_protocol"));
            return propertyList;
        }
    });
});
