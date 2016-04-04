define([
    "dcl/dcl",
    "common/cert-build-list-selects"
], function (declare, ListSelects) {
    "use strict";

    return declare(ListSelects, {
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
        })
    });

});
