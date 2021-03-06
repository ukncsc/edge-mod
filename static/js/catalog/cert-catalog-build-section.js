define([
    "dcl/dcl",
    "knockout",
    "catalog/cert-catalog-revisions",
    "catalog/cert-catalog-activity",
    "catalog/cert-catalog-matching",
    "catalog/cert-catalog-purge"
], function (declare, ko, Revisions, Activity, Matching, Purge) {
    "use strict";
    function indexBy(items, pname) {
        var indexed = {};
        ko.utils.arrayForEach(items(), function (item) {
            indexed[item()[pname]()] = item;
        });
        return indexed;
    }

    return declare(null, {
        declaredClass: "CatalogSection",
        constructor: function () {
            this.options = ko.observableArray([
                ko.observable(new Revisions()),
                ko.observable(new Activity()),
                ko.observable(new Matching()),
                ko.observable(new Purge())
            ]);
            this._byLabel = indexBy(this.options, "label");
            this.value = ko.observable(
                this.options()[0]()
            );
        },

        loadStatic: function (optionLists) {
            ko.utils.arrayForEach(this.options(), function (option) {
                option().loadStatic(optionLists);
            });
        },

        findByLabel: function (label) {
            return this._byLabel[label];
        }
    });
});
