define([
    "dcl/dcl",
    "knockout",
    "common/cert-build-list-selects",
    "common/cert-build-functions"
], function (declare, ko, listSelects, buildFunctions) {
    "use strict";

    function DiscoveryMethods() {
        DiscoveryMethods.super.constructor.call(this, "Discovery Methods", {
            selectChoice: 'discovery_methods_list',
            saveKey: 'discovery_methods'
        });
    }

    buildFunctions.extend(DiscoveryMethods, listSelects);

    return  DiscoveryMethods;
});
