define([
    "dcl/dcl",
    "common/cert-build-list-idents"
], function (declare, listIdents) {
    "use strict";

    return declare(listIdents, {
        declaredClass: "Victims",
        constructor: declare.superCall(function (sup) {
            return function () {
                sup.call(this, "Victims", {
                    saveKey: 'victims',
                    required: true,
                    displayName: 'Victim'
                });
            }
        })
    });
});
