define([
    "dcl/dcl",
    "common/cert-build-related"
], function (declare, buildRelated) {
    "use strict";

    return declare(buildRelated, {
        declaredClass: "RelatedIndicators",

        constructor: declare.superCall(function (sup) {
            return function() {
                sup.call(this, "Related Indicators", {
                    itemType: 'ind',
                    saveKey: 'related_indicators',
                    required: false,
                    displayName: 'Related Indicator'
                });
            }
        })
    });
});
