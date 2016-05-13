define([
    "knockout",
    "dcl/dcl"
], function (ko, declare) {
    "use strict";

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
                if(this.totalResults() == 0) {
                    return 1;
                } else{
                     return Math.ceil(this.totalResults() / this.resultsPerPage());
                }
            }, this);

            this.searchTerm = ko.observable('').extend({rateLimit: {timeout: 300, method: "notifyWhenChangesStop"}});
            this.searchTerm.subscribe(function () {
                this.currentPage(1);
            }, this);
            this.currentPage.subscribe(function () {
                this.results.refresh();
            }, this);
            this.showAll = ko.observable(false);
            this.searching = ko.observable(false);
            this.showAll.subscribe(function() {
                this.currentPage(1);
            },this)
        },

        retrieve: function () {
            this.searching(true);
            var params = {
                type: this.itemType,
                size: this.resultsPerPage(),
                offset: (this.currentPage() - 1) * this.resultsPerPage(),
                search: this.searchTerm(),
                showAll: this.showAll()
            };
            postJSON(this.getUrl, params, function (d) {
                this.results(d.data);
                this.totalResults(d.count);
                this.searching(false);
                }.bind(this));
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
