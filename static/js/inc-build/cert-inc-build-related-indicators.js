define([
    "dcl/dcl",
    "knockout",
    "common/cert-build-related",
    "common/cert-build-functions"
], function (declare, ko, buildRelated, buildFunctions) {
    "use strict";

    function RelatedIndicators() {
        RelatedIndicators.super.constructor.call(this, "Related Indicators", {
            resultsPerPage: 10,
            itemType: 'ind',
            saveKey: 'related_indicators',
            getUrl: '/catalog/ajax/load_catalog/',
            candidateItemsTemplate: 'candidateModal',
            itemTemplate: 'relatedItem'
        });
    }

    buildFunctions.extend(RelatedIndicators, buildRelated);

    return  RelatedIndicators;
});
