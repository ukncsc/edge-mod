define([
    "dcl/dcl",
    "knockout",
    "ind-build/indicator-builder-shim",
    "common/cert-build-candidate-related-items"
], function (declare, ko, indicator_builder, candidateRelatedItems) {
    "use strict";
    var CERTCandidateRelatedItems = candidateRelatedItems;
    indicator_builder.CandidateRelatedItems = CERTCandidateRelatedItems;

    return CERTCandidateRelatedItems;
});
