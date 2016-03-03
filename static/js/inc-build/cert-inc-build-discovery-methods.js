define([
    "dcl/dcl",
    "common/cert-build-list-selects"
], function (declare, ListSelects) {
    "use strict";

    return declare(ListSelects, {
        declaredClass: "DiscoveryMethods",

        constructor: declare.superCall(function (sup) {
            return function () {
                sup.call(this, "Discovery Methods", {
                    selectChoice: 'discovery_methods_list',
                    saveKey: 'discovery_methods',
                    required: true,
                    displayName: 'Discovery Method'
                });
            }
        })
    });

});
