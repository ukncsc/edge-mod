define([
    "dcl/dcl",
    "knockout",
    "common/cert-build-related",
    "common/cert-build-functions"
], function (declare, ko, buildRelated, buildFunctions) {
    "use strict";

    function LeveragedTTPs() {
        LeveragedTTPs.super.constructor.call(this, "Leveraged TTPs", {
            resultsPerPage: 10,
            itemType: 'ttp',
            saveKey: 'leveraged_ttps',
            getUrl: '/catalog/ajax/load_catalog/',
            candidateItemsTemplate: 'candidateModal',
            itemTemplate: 'relatedItem'
        });
    }

    buildFunctions.extend(LeveragedTTPs, buildRelated);

   return  LeveragedTTPs;
});
