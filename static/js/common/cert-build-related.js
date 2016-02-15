define([
    "../dcl/dcl",
    "knockout",
    "common/cert-abstract-builder-form",
    "common/cert-build-candidate-related-items",
    "common/cert-build-functions"
], function (declare, ko, AbstractBuilderForm, CandidateRelatedItems, buildFunctions) {
    "use strict";

    function scrollToTop() {
        document.getElementById("content").scrollTop = 0;
    }

    function RelatedItems (label, options) {
        RelatedItems.super.constructor.apply(this, [ label ]);
        this.relatedItems = ko.observableArray([]);
        this.totalItems = ko.computed(function () {
            return this.relatedItems().length;
        }, this);
        this.currentPage = ko.observable(0);
        this.numPages = ko.computed(function () {
            return Math.ceil(this.relatedItems().length / this.resultsPerPage);
        }, this);
        this.paginationHUD = ko.computed(function () {
            var totalItems = this.totalItems();
            return "Page " + (this.currentPage() + 1) + " of " + this.numPages() + " (" +
                totalItems + " row" + (totalItems === 1 ? ")" : "s)");
        }, this);
        this.pageItems = ko.computed(function() {
            var currentPage = this.currentPage();
            var start = this.resultsPerPage * currentPage;
            var end = this.resultsPerPage * (currentPage + 1);
            return this.relatedItems.slice(start, end);
        }, this);
        this.count = ko.computed(function () {
            return this.relatedItems().length || "";
        }, this);
        this.resultsPerPage = options['resultsPerPage'];
        this.itemType = options['itemType'];
        this.saveKey = options['saveKey'];
        this.getUrl = options['getUrl'];
        this.candidateItemsTemplate = options['candidateItemsTemplate'];
        this.itemTemplate = options['itemTemplate'];
        this.modalWidth = options['modalWidth'] || 800;
        this.modalHeight = options['modalHeight'] || 500;
    }

    buildFunctions.extend(RelatedItems, AbstractBuilderForm);

    RelatedItems.prototype.save = function() {
        var data = {};
        data[this.saveKey] = this.relatedItems();
        return data;
    };

    RelatedItems.prototype.load = function(data) {
        this.relatedItems(data[this.saveKey] || []);
    };

    RelatedItems.prototype.removeRelatedItem = function(item) {
        this.relatedItems.remove(item);
    };

    RelatedItems.prototype.getCandidateItemsViewModel = function() {
        return new CandidateRelatedItems(
            this.resultsPerPage,
            this.itemType,
            this.getUrl
        );
    };

    RelatedItems.prototype.showCandidateItems = function() {
        var self = this;

        var targetDiv = document.createElement("div");
        targetDiv.style.display = "none";
        document.body.appendChild(targetDiv);

        var candidateRelatedItems = this.getCandidateItemsViewModel();

        ko.renderTemplate(
            self.candidateItemsTemplate,
            candidateRelatedItems,
            {
                afterRender: function(nodes) {
                    // Get the modal:
                    var modalElements = nodes.filter(function(node) {
                        return node.nodeType === 1; // Ignore text
                    });
                    var modal = $(modalElements);

                    // Ensure it always removes itself from the DOM when closed, and clean up the KO bindings:
                    modal.on("hidden.bs.modal", function () {
                        candidateRelatedItems.reset();
                        modal.each(function (index, element) { ko.cleanNode(element); });
                        modal.remove();
                    });

                    // Show it:
                    modal.modal({ width: self.modalWidth, height: self.modalHeight, show: true});

                    // Allow the viewmodel to close the modal:
                    candidateRelatedItems.modal = {
                        close: function() {
                            self.relatedItems.push.apply(self.relatedItems, candidateRelatedItems.selectedItems());
                            modal.modal('hide');
                        },
                        cancel: function() {
                            modal.modal('hide');
                        }
                    };
                }
            },
            targetDiv,
            "replaceNode"
        );
    };

    RelatedItems.prototype.hasPrev = function() {
        return this.currentPage() > 0;
    };

    RelatedItems.prototype.prevPage = function() {
        this.currentPage(this.currentPage() - 1);
        scrollToTop();
    };

    RelatedItems.prototype.firstPage = function() {
        this.currentPage(0);
        scrollToTop();
    };

    RelatedItems.prototype.hasNext = function() {
        return this.currentPage() + 1 < this.numPages();
    };

    RelatedItems.prototype.nextPage = function() {
        this.currentPage(this.currentPage() + 1);
        scrollToTop();
    };

    RelatedItems.prototype.lastPage = function() {
        this.currentPage(this.numPages() - 1);
        scrollToTop();
    };

    return  RelatedItems;
});
