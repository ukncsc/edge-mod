define([
    "dcl/dcl",
    "knockout",
    "catalog/cert-catalog-revisions",
    "catalog/cert-catalog-activity"
], function (declare, ko, Revisions, Activity) {
    "use strict";
    function indexBy(items, pname) {
        var indexed = {};
        ko.utils.arrayForEach(items(), function (item) {
            indexed[item()[pname]()] = item;
        });
        return indexed;
    }

    return declare(null, {
        declaredClass: "Catalog-Section",
        constructor: function () {
            this.options = ko.observableArray([
                ko.observable(new Revisions()),
                ko.observable(new Activity())
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
