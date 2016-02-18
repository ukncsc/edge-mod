define([
    "dcl/dcl",
    "knockout",
    "common/cert-build-related"
], function (declare, ko, buildRelated) {
    "use strict";

    var RelatedObservables = declare(buildRelated, {
        declaredClass: "RelatedObservables",

        constructor: declare.superCall(function (sup) {
            return function() {
                sup.call(this, "Related Observables", {
                    resultsPerPage: 10,
                    itemType: 'inc',
                    saveKey: 'related_observables',
                    getUrl: '/catalog/ajax/load_catalog/',
                    candidateItemsTemplate: 'candidateModal',
                    itemTemplate: 'relatedItem'
                });
            }
        })
    });

    return  RelatedObservables;
});
