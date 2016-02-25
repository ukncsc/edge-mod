define([
    "dcl/dcl",
    "knockout",
    "common/cert-build-list-idents"
], function (declare, ko, listIdents) {
    "use strict";

    var Responders = declare(listIdents, {
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

    return  Responders;
});
