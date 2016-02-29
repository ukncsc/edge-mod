define([
    "dcl/dcl",
    "common/cert-build-list-idents"
], function (declare, listIdents) {
    "use strict";

    return declare(listIdents, {
        declaredClass: "Responders",
        constructor: declare.superCall(function (sup) {
            return function () {
                sup.call(this, "Responders", {
                    saveKey: 'responders',
                    required: true,
                    displayName: 'Responder'
                });
            }
        })
    });
});
