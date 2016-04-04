define([
    "dcl/dcl",
    "common/cert-build-related"
], function (declare, BuildRelated) {
    "use strict";

    return declare(BuildRelated, {
        declaredClass: "LeveragedTTPs",

        constructor: declare.superCall(function (sup) {
            return function () {
                sup.call(this, "Leveraged TTPs", {
                    itemType: 'ttp',
                    saveKey: 'leveraged_ttps',
                    required: true,
                    displayName: 'Leveraged TTP'
                });
            }
        })
    });

});
