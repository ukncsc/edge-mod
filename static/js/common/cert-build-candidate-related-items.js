define([
    "knockout"
], function (ko) {
    "use strict";

    function CandidateRelatedItems (resultsPerPage, itemType, getUrl) {
        this.itemType = itemType;
        this.getUrl = getUrl;

        this.results = ko.onDemandObservable(this.retrieve, this);
        this.selectedItems = ko.observableArray([]);

        this.resultsPerPage = ko.observable(resultsPerPage);
        this.currentPage = ko.observable(1).extend({ notify: 'always' });
        this.totalResults = ko.observable(0);
        this.totalPages = ko.computed(function() {
            return Math.ceil(this.totalResults() / this.resultsPerPage());
        }, this);

        this.searchTerm = ko.observable('').extend({ rateLimit: { timeout: 300, method: "notifyWhenChangesStop" } });
        this.searchTerm.subscribe(function() {
           this.currentPage(1);
        }, this);
        this.currentPage.subscribe(function() {
            this.results.refresh();
        }, this);
    }

    CandidateRelatedItems.prototype.retrieve = function() {
        var params = {
            type: this.itemType,
            size: this.resultsPerPage(),
            offset: (this.currentPage()-1) * this.resultsPerPage(),
            search: this.searchTerm()
        };
        postJSON(this.getUrl, params, function(d) {
            this.totalResults(d.count);
            this.results(d.data);
        }.bind(this));
    };

    CandidateRelatedItems.prototype.reset = function () {
        this.selectedItems([]);
    };

    CandidateRelatedItems.prototype.selectItem = function(item) {
        this.selectedItems.push({ idref: item['id'], view_url: item['view_url'] });
        this.modal.close();
    };

    CandidateRelatedItems.prototype.cancel = function() {
        this.modal.cancel();
    };

    CandidateRelatedItems.prototype.goFirst = function() {
        this.currentPage(1);
    };

    CandidateRelatedItems.prototype.goPrev = function() {
        this.currentPage(this.currentPage() - 1);
    };

    CandidateRelatedItems.prototype.goNext = function() {
        this.currentPage(this.currentPage() + 1);
    };

    CandidateRelatedItems.prototype.goLast = function() {
        this.currentPage(this.totalPages());
    };

    return CandidateRelatedItems;
});

