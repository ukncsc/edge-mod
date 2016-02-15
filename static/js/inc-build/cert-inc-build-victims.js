define([
    "dcl/dcl",
    "knockout",
    "common/cert-build-list-idents",
    "common/cert-build-functions"
], function (declare, ko, listIdents, buildFunctions) {
    "use strict";

    function Victims() {
        Victims.super.constructor.call(this, "Victims", {
            saveKey: 'victims'
        });
    }

    buildFunctions.extend(Victims, listIdents);

    return  Victims;
});
