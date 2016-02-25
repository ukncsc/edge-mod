define([
    "dcl/dcl",
    "knockout",
    "common/cert-build-related"
], function (declare, ko, buildRelated) {
    "use strict";

    var AttributedActors = declare(buildRelated, {
        declaredClass: "AttributedActors",

        constructor: declare.superCall(function (sup) {
            return function() {
                sup.call(this, "Attributed Actors", {
                    resultsPerPage: 10,
                    itemType: 'act',
                    saveKey: 'attributed_actors',
                    getUrl: '/catalog/ajax/load_catalog/',
                    candidateItemsTemplate: 'candidateModal',
                    itemTemplate: 'relatedItem',
                    required: true,
                    displayName: 'Attributed Actor'
                });
            }
        })
    });

    return  AttributedActors;
});
