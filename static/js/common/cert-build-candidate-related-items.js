define([
    "knockout",
    "dcl/dcl",
    "inc-build/cert-incident-builder-shim"
], function (ko, declare, incident_builder) {
    "use strict";
    var id_ns = incident_builder.id_ns || "";
    return declare(null, {
        declaredClass: "CandidateRelatedItems",

        constructor: function (resultsPerPage, itemType, getUrl) {
            this.itemType = itemType;
            this.getUrl = getUrl;

            this.results = ko.onDemandObservable(this.retrieve, this);
            this.selectedItems = ko.observableArray([]);

            this.resultsPerPage = ko.observable(resultsPerPage);
            this.currentPage = ko.observable(1).extend({notify: 'always'});
            this.totalResults = ko.observable(0);
            this.totalPages = ko.computed(function () {
                return Math.ceil(this.totalResults() / this.resultsPerPage());
            }, this);

            this.searchTerm = ko.observable('').extend({rateLimit: {timeout: 300, method: "notifyWhenChangesStop"}});
            this.searchTerm.subscribe(function () {
                this.currentPage(1);
            }, this);
            this.currentPage.subscribe(function () {
                this.results.refresh();
            }, this);
            this.CERTonly = ko.observable(true);
            this.searching = ko.observable(false);
        },

        retrieve: function () {
            this.searching(true);
            var params = {
                type: this.itemType,
                size: this.resultsPerPage(),
                offset: (this.currentPage() - 1) * this.resultsPerPage(),
                search: this.searchTerm()
            };
            postJSON(this.getUrl, params, function (d) {
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
                this.searching(false);
                }.bind(this));
        },

        toggleRelatedItems: function() {
            if(this.CERTonly()){
                this.CERTonly(false)
            }
            else {
                this.CERTonly(true)
            }
            this.retrieve()
        },

        reset: function () {
            this.selectedItems([]);
        },

        selectItem: function (item) {
            this.selectedItems.push({idref: item['id'], view_url: item['view_url']});
            this.modal.close();
        },

        cancel: function () {
            this.modal.cancel();
        },

        goFirst: function () {
            this.currentPage(1);
        },

        goPrev: function () {
            this.currentPage(this.currentPage() - 1);
        },

        goNext: function () {
            this.currentPage(this.currentPage() + 1);
        },

        goLast: function () {
            this.currentPage(this.totalPages());
        }
    })
});
