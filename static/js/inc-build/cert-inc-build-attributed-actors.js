define([
    "dcl/dcl",
    "knockout",
    "common/cert-build-related",
    "common/cert-build-functions"
], function (declare, ko, buildRelated, buildFunctions) {
    "use strict";

    function AttributedActors() {
        AttributedActors.super.constructor.call(this, "Attributed Actors", {
            resultsPerPage: 10,
            itemType: 'act',
            saveKey: 'attributed_actors',
            getUrl: '/catalog/ajax/load_catalog/',
            candidateItemsTemplate: 'candidateModal',
            itemTemplate: 'relatedItem'
        });
    }

    buildFunctions.extend(AttributedActors, buildRelated);

    return AttributedActors;
});
