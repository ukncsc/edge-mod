define([
    "dcl/dcl",
    "knockout",
    "common/cert-build-list-idents",
    "common/cert-build-functions"
], function (declare, ko, listIdents, buildFunctions) {
    "use strict";

    function Responders() {
        Responders.super.constructor.call(this, "Responders", {
            saveKey: 'responders'
        });
    }

    buildFunctions.extend(Responders, listIdents);

    return  Responders;
});
