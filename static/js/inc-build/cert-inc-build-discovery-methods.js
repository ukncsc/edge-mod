define([
    "dcl/dcl",
    "knockout",
    "common/cert-build-list-selects"
], function (declare, ko, listSelects) {
    "use strict";


    var DiscoveryMethods = declare(listSelects, {
        declaredClass: "DiscoveryMethods",

        constructor: declare.superCall(function (sup) {
                return function () {
                    sup.call(this, "Discovery Methods", {
                        selectChoice: 'discovery_methods_list',
                        saveKey: 'discovery_methods'
                    });
                }
            }
        )
    });

    return  DiscoveryMethods;
});
