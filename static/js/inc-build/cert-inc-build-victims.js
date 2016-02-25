define([
    "dcl/dcl",
    "knockout",
    "common/cert-build-list-idents"
], function (declare, ko, listIdents) {
    "use strict";

    var Victims = declare(listIdents, {
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

    return  Victims;
});
