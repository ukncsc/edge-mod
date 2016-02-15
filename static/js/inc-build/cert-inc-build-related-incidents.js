define([
    "dcl/dcl",
    "knockout",
    "common/cert-build-related",
    "common/cert-build-functions"
], function (declare, ko, buildRelated, buildFunctions) {
    "use strict";

    function RelatedIncidents() {
        RelatedIncidents.super.constructor.call(this, "Related Incidents", {
            resultsPerPage: 10,
            itemType: 'inc',
            saveKey: 'related_incidents',
            getUrl: '/catalog/ajax/load_catalog/',
            candidateItemsTemplate: 'candidateModal',
            itemTemplate: 'relatedItem'
        });
    }

    buildFunctions.extend(RelatedIncidents, buildRelated);

    return  RelatedIncidents;
});
