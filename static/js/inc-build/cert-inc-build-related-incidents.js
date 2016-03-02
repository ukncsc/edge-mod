define([
    "dcl/dcl",
    "common/cert-build-related"
], function (declare, buildRelated) {
    "use strict";

    return declare(buildRelated, {
        declaredClass: "RelatedIncidents",

        constructor: declare.superCall(function (sup) {
            return function() {
                sup.call(this, "Related Incidents", {
                    itemType: 'inc',
                    saveKey: 'related_incidents',
                    required: false,
                    displayName: 'Related Incident'
                });
            }
        })
    });
});
