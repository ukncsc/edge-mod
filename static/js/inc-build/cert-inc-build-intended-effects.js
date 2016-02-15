define([
    "dcl/dcl",
    "knockout",
    "common/cert-build-list-selects",
    "common/cert-build-functions"
], function (declare, ko, listSelects, buildFunctions) {
    "use strict";
    "use strict";

    function IntendedEffects() {
        IntendedEffects.super.constructor.call(this, "Intended Effects", {
            selectChoice: 'intended_effects_list',
            saveKey: 'intended_effects'
        });
    }

    buildFunctions.extend(IntendedEffects, listSelects);

    return  IntendedEffects;
});
