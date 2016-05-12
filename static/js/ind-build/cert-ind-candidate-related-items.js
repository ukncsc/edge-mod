define([
    "dcl/dcl",
    "knockout",
    "ind-build/indicator-builder-shim"
], function (declare, ko, indicator_builder) {
    "use strict";
    var CERTCandidateRelatedItems =  declare(indicator_builder.CandidateRelatedItems, {
        declaredClass: "CERTCandidateRelatedItems",
        constructor: declare.superCall(function (sup) {
            return function (resultsPerPage, itemType) {
                sup.call(this, resultsPerPage, itemType);
                this.getUrl = '/adapter/certuk_mod/ajax/load_catalog/';
                this.showAll = ko.observable(false);
                this.searching = ko.observable(false);
                this.totalPages = ko.computed(function () {
                if(this.totalResults() == 0) {
                    return 1;
                } else{
                     return Math.ceil(this.totalResults() / this.resultsPerPage());
                }
            }, this);
                this.showAll.subscribe(function() {
                    this.currentPage(1);
                    this.retrieve();
                }, this)
            }
        }),

        retrieve: declare.superCall(function (sup){
            return function(){
                this.searching(true);
                var params = {
                    type: this.itemType,
                    size: this.resultsPerPage(),
                    offset: (this.currentPage()-1) * this.resultsPerPage(),
                    search: this.searchTerm(),
                    showAll: this.showAll()
                };
                postJSON(this.getUrl, params, function(d) {
                    this.results(d.data);
                    this.totalResults(d.count);
                    this.searching(false);
                }.bind(this));
            }
        })

    });

    indicator_builder.CandidateRelatedItems = CERTCandidateRelatedItems;
    return CERTCandidateRelatedItems;
});
