define([
    "dcl/dcl",
    "knockout",
    "common/cert-build-related",
    "common/cert-build-functions"
], function (declare, ko, buildRelated, buildFunctions) {
    "use strict";

    function RelatedObservables() {
        RelatedObservables.super.constructor.call(this, "Related Observables", {
            resultsPerPage: 10,
            itemType: 'obs',
            saveKey: 'related_observables',
            getUrl: '/catalog/ajax/load_catalog/',
            candidateItemsTemplate: 'candidateModal',
            itemTemplate: 'relatedItem'
        });
    }

    buildFunctions.extend(RelatedObservables, buildRelated);

    return  RelatedObservables;
});
