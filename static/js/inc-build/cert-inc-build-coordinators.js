define([
    "dcl/dcl",
    "common/cert-build-list-idents"
], function (declare, listIdents) {
    "use strict";

    return declare(listIdents, {
        declaredClass: "Coordinators",
        constructor: declare.superCall(function (sup) {
            return function () {
                sup.call(this, "Coordinators", {
                    saveKey: 'coordinators',
                    required: true,
                    displayName: 'Coordinator',
                    saveGroup:'identity'
                });
            }
        })
    });
});
