define([
    "dcl/dcl",
    "knockout",
    "common/cert-build-list-selects"
], function (declare, ko, listSelects) {
    "use strict";

        var IntendedEffects = declare(listSelects, {
        declaredClass: "IntendedEffects",

        constructor: declare.superCall(function (sup) {
                return function () {
                    sup.call(this, "Intended Effects", {
                        selectChoice: 'intended_effects_list',
                        saveKey: 'intended_effects',
                        required: true,
                        displayName: 'Intended Effect'
                    });
                }
            }
        )
    });

     return IntendedEffects;
});
