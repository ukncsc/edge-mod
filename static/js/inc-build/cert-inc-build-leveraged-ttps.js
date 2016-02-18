define([
    "dcl/dcl",
    "knockout",
    "common/cert-build-related"
], function (declare, ko, buildRelated) {
    "use strict";

    var LeveragedTTPs = declare(buildRelated, {
        declaredClass: "LeveragedTTPs",

        constructor: declare.superCall(function (sup) {
            return function() {
                sup.call(this, "Leveraged TTPs", {
                    resultsPerPage: 10,
                    itemType: 'inc',
                    saveKey: 'leveraged_ttps',
                    getUrl: '/catalog/ajax/load_catalog/',
                    candidateItemsTemplate: 'candidateModal',
                    itemTemplate: 'relatedItem'
                });
            }
        })
    });

    return  LeveragedTTPs;
});
