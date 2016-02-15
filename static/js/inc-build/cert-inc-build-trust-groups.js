define([
    "dcl/dcl",
    "knockout",
    "common/cert-build-list-selects",
    "common/cert-build-functions"
], function (declare, ko, listSelects, buildFunctions) {
    "use strict";

    function TrustGroups() {
        TrustGroups.super.constructor.call(this, "Trust Groups", {
            selectChoice: 'trustgroups_list',
            saveKey: 'trustgroups'
        });
    }

    buildFunctions.extend(TrustGroups, listSelects);

    return  TrustGroups;
});
