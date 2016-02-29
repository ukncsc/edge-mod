define([
    "dcl/dcl",
    "common/cert-build-list-selects"
], function (declare, ListSelects) {
    "use strict";

    return declare(ListSelects, {
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
            })
    });

});
