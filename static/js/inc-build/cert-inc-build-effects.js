define([
    "dcl/dcl",
    "knockout",
    "common/cert-build-list-selects",
    "common/cert-build-functions"
], function (declare, ko, listSelects, buildFunctions) {
    "use strict";

    function Effects() {
        Effects.super.constructor.call(this, "Effects", {
            selectChoice: 'effects_list',
            saveKey: 'effects'
        });
    }

    buildFunctions.extend(Effects, listSelects);

     return Effects;
});
