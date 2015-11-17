define([
    "dcl/dcl",
    "./NamedProperty",
    "./StixObjectType"
], function (declare, NamedProperty, StixObjectType) {
    "use strict";

    return declare(StixObjectType, {
        declaredClass: "HttpSession",
        properties: function () {
            var propertyList = [];
            NamedProperty.addToPropertyList(
                propertyList,
                "User Agent",
                this.stixPackage.safeValueGet(
                    this.id,
                    this.data,
                    "http_request_response.0.http_client_request.http_request_header.parsed_header.user_agent",
                    "user_agent"
                )
            );
            return propertyList;
        }
    });
});
