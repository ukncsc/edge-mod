define([
    "dcl/dcl",
    "knockout",
    "ind-build/indicator-builder-shim"
], function (declare, ko, indicator_builder) {
    "use strict";
    var id_ns = indicator_builder.id_ns || "";
    var CERTCandidateRelatedItems =  declare(indicator_builder.CandidateRelatedItems, {
        declaredClass: "CERTCandidateRelatedItems",
        constructor: declare.superCall(function (sup) {
            return function (resultsPerPage, itemType, getUrl) {
                sup.call(this, resultsPerPage, itemType, getUrl);
                this.CERTonly = ko.observable(true);
            }
        }),

        retrieve: declare.superCall(function (sup){
            return function(){
                var params = {
                    type: this.itemType,
                    size: this.resultsPerPage(),
                    offset: (this.currentPage()-1) * this.resultsPerPage(),
                    search: this.searchTerm()
                };
                postJSON(this.getUrl, params, function(d) {
                    var newData = [];
                    if(d.count!=0 && this.CERTonly()){
                        for(var i=0; i< d.data.length; i++) {
                            if (d.data[i].idns == id_ns) {
                                newData.push(d.data[i])
                            }
                            this.results(newData);
                            this.totalResults(newData.length);
                        }
                    }
                    else {
                        this.results(d.data);
                        this.totalResults(d.count);
                    }
                }.bind(this));
            }
        }),

        toggleRelatedItems: function() {
            if(this.CERTonly()){
                this.CERTonly(false)
            }
            else {
                this.CERTonly(true)
            }
            this.retrieve()
        }

    });

    indicator_builder.CandidateRelatedItems = CERTCandidateRelatedItems;
    return CERTCandidateRelatedItems;
});
