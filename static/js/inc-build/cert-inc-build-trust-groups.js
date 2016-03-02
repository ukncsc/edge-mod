define([
    "dcl/dcl",
    "knockout",
    "common/cert-build-list-selects"
], function (declare, ko, listSelects) {
    "use strict";

    var TrustGroups = declare(listSelects, {
        declaredClass: "TrustGroups",

        constructor: declare.superCall(function (sup) {
                return function () {
                    sup.call(this, "Trust Groups", {
                        selectChoice: 'trustgroups_list',
                        saveKey: 'trustgroups',
                        required: true,
                    displayName: 'Trust Group'
                    });

                }
            }
        )
    });

    return TrustGroups;
});
