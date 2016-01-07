define([
    "dcl/dcl",
    "knockout",
    "stix/StixPackage",
    "kotemplate!duplicates-type-selector:./templates/duplicates_type_selector.html",
    "kotemplate!duplicates-original-selector:./templates/duplicates_original_selector.html",
    "kotemplate!duplicates-duplicate-selector:./templates/duplicates_duplicate_selector.html",
    "kotemplate!duplicates-preview:./templates/duplicates_preview.html"
], function (declare, ko, StixPackage) {
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
    var rate_limited = Object.freeze({rateLimit: {timeout: 50, method: "notifyWhenChangesStop"}});

    function fromArray(srcArray, idx) {
        return srcArray instanceof Array && srcArray.length > idx ? srcArray[idx] : null;
    }

    function buildLabel(baseText, pluralText, count) {
        return count < 2 ? baseText : baseText + pluralText + " (" + count + ")";
    }

    return declare(null, {
        declaredClass: "DuplicateModel",
        constructor: function (duplicates) {
            this.duplicates = function () {
                return duplicates;
            };

            this.selectedType = ko.observable(null);
            this.originalsLabel = ko.observable("Original");
            this.selectedOriginalId = ko.observable(null).extend(rate_limited);
            this.selectedOriginal = ko.observable(null);
            this.duplicatesLabel = ko.observable("Duplicate");
            this.selectedDuplicateId = ko.observable(null).extend(rate_limited);
            this.selectedDuplicate = ko.observable(null);

            this.typesWithDuplicates = ko.computed(function () {
                var typesWithDuplicates = [];
                // TODO: sort: Indicator, Observable, TTP, then alphabetic
                ko.utils.objectForEach(this.duplicates(), function (key, value) {
                    var numDups = Object.keys(value).length;
                    if (numDups > 0) {
                        typesWithDuplicates.push({type: key, label: buildLabel(type_labels[key], "", numDups)});
                    }
                });
                return typesWithDuplicates;
            }, this);
            this.originalsForType = ko.computed(function () {
                var selectedType = this.selectedType();
                var originals = selectedType ? Object.keys(this.duplicates()[selectedType]) : [];
                this.originalsLabel(buildLabel("Original", "s", originals.length));
                this.selectedOriginalId(fromArray(originals, 0));
                return originals;
            }, this);
            this.duplicatesForOriginal = ko.computed(function () {
                var selectedType = this.selectedType();
                var selectedOriginalId = this.selectedOriginalId();
                var duplicates = selectedType && selectedOriginalId ? this.duplicates()[selectedType][selectedOriginalId] : [];
                this.duplicatesLabel(buildLabel("Duplicate", "s", duplicates.length));
                this.selectedDuplicateId(fromArray(duplicates, 0));
                return duplicates;
            }, this);

            this.selectedOriginalId.subscribe(this._onOriginalChanged, this);
            this.selectedDuplicateId.subscribe(this._onDuplicateChanged, this);
        },

        _onOriginalChanged: function (newId) {
            if (typeof newId === "string") {
                getJSON("/adapter/certuk_mod/duplicates/object/" + newId, null, function (data) {
                    this.selectedOriginal(new StixPackage(data["package"], data["root_id"]));
                }.bind(this));
            } else {
                this.selectedOriginal(null);
            }
        },

        _onDuplicateChanged: function (newId) {
            if (typeof newId === "string") {
                getJSON("/adapter/certuk_mod/duplicates/object/" + newId, null, function (data) {
                    this.selectedDuplicate(new StixPackage(data["package"], data["root_id"]));
                }.bind(this));
            } else {
                this.selectedDuplicate(null);
            }
        }
    });
});
