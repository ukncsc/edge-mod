define([
    "dcl/dcl",
    "common/cert-build-list-selects"
], function (declare, ListSelects) {
    "use strict";

    return declare(ListSelects, {
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
        })
    });

});
