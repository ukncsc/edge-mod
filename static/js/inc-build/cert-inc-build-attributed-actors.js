define([
    "dcl/dcl",
    "common/cert-build-related"
], function (declare, BuildRelated) {
    "use strict";

    return declare(BuildRelated, {
        declaredClass: "AttributedActors",

        constructor: declare.superCall(function (sup) {
            return function () {
                sup.call(this, "Attributed Actors", {
                    itemType: 'act',
                    saveKey: 'attributed_actors',
                    required: true,
                    displayName: 'Attributed Actor'
                });
            }
        })
    });
});
