define([
    "dcl/dcl",
    "knockout",
    "common/cert-build-list-selects"
], function (declare, ko, listSelects) {
    "use strict";

    var Effects = declare(listSelects, {
        declaredClass: "Effects",

        constructor: declare.superCall(function (sup) {
                return function () {
                    sup.call(this, "Effects", {
                        selectChoice: 'effects_list',
                        saveKey: 'effects',
                        required: true,
                        displayName: 'Effect'
                    });

                }
            }
        )
    });

    return Effects;
});
