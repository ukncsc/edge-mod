define([
    "dcl/dcl",
    "knockout",
    "common/cert-build-related"
], function (declare, ko, buildRelated) {
    "use strict";

    var RelatedIncidents = declare(buildRelated, {
        declaredClass: "RelatedIncidents",

        constructor: declare.superCall(function (sup) {
            return function() {
                sup.call(this, "Related Incidents", {
                    resultsPerPage: 10,
                    itemType: 'inc',
                    saveKey: 'related_incidents',
                    getUrl: '/catalog/ajax/load_catalog/',
                    candidateItemsTemplate: 'candidateModal',
                    itemTemplate: 'relatedItem',
                    required: true,
                    displayName: 'Related Incident'
                });
            }
        })
    });

    return  RelatedIncidents;
});
