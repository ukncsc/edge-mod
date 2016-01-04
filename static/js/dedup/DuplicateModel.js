define([
    "dcl/dcl",
    "knockout",
    "kotemplate!duplicates-view:./templates/duplicates-view.html"
], function (declare, ko) {
    "use strict";

    var type_labels = Object.freeze({
        "ind": "Indicator",
        "obs": "Observable",
        "act": "Threat Actor",
        "ttp": "TTP",
        "cam": "Campaign",
        "inc": "Incident",
        "coa": "Course Of Action",
        "tgt": "Exploit Target",
        "pkg": "Package"
    });

    return declare(null, {
        declaredClass: "DuplicateModel",
        constructor: function (duplicates) {
            this.duplicates = ko.observable(duplicates);

            this.selectedType = ko.observable(null);
            this.selectedOriginal = ko.observable(null);

            this.typesWithDuplicates = ko.computed(function () {
                var typesWithDuplicates = [];
                ko.utils.objectForEach(this.duplicates(), function (key, value) {
                    if (Object.keys(value).length > 0) {
                        typesWithDuplicates.push({type: key, label: type_labels[key]})
                    }
                });
                return typesWithDuplicates;
            }, this);
            this.originalsForType = ko.computed(function () {
                return this.selectedType()
                    && Object.keys(this.duplicates()[this.selectedType()]);
            }, this);
            this.duplicatesForOriginal = ko.computed(function () {
                return this.selectedType()
                    && this.selectedOriginal()
                    && this.duplicates()[this.selectedType()][this.selectedOriginal()];
            }, this);
        }
    });
});
