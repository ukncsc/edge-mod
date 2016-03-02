define([
    "dcl/dcl",
    "common/cert-build-related"
], function (declare, buildRelated) {
    "use strict";

    return declare(buildRelated, {
        declaredClass: "RelatedObservables",

        constructor: declare.superCall(function (sup) {
            return function() {
                sup.call(this, "Related Observables", {
                    itemType: 'obs',
                    saveKey: 'related_observables',
                    required: false,
                    displayName: 'Related Observable'
                });
            }
        })
    });
});
