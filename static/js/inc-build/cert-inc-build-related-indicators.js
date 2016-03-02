define([
    "dcl/dcl",
    "knockout",
    "common/cert-build-related"
], function (declare, ko, buildRelated) {
    "use strict";

    var RelatedIndicators = declare(buildRelated, {
        declaredClass: "RelatedIndicators",

        constructor: declare.superCall(function (sup) {
            return function() {
                sup.call(this, "Related Indicators", {
                    resultsPerPage: 10,
                    itemType: 'ind',
                    saveKey: 'related_indicators',
                    getUrl: '/catalog/ajax/load_catalog/',
                    candidateItemsTemplate: 'candidateModal',
                    itemTemplate: 'relatedItem',
                    required: true,
                    displayName: 'Related Indicator'
                });
            }
        })
    });

    return  RelatedIndicators;
});
