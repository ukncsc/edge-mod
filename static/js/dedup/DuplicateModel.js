define([
    "dcl/dcl",
    "knockout",
    "stix/StixPackage",
    "kotemplate!duplicates-type-selector:./templates/duplicates_type_selector.html",
    "kotemplate!duplicates-original-selector:./templates/duplicates_original_selector.html",
    "kotemplate!duplicates-duplicate-selector:./templates/duplicates_duplicate_selector.html",
    "kotemplate!duplicates-preview:./templates/duplicates_preview.html",
    "kotemplate!duplicates-analyse:./templates/duplicates_analyse.html",
    "kotemplate!duplicates-analyse-table:./templates/duplicates_analyse_table.html"
], function (declare, ko, StixPackage) {
    "use strict";
/*
analysisStatus':
    1 - Analyse and Merge options
    2 - Analysis/Merging
    3 - Show Backlinks Table
    4 - Show Merge Result
    5 - Show Error Result
 */
    var type_labels = Object.freeze({
        //"ind": "Indicator",
        "obs": "Observable",
        "ttp": "TTP",
        //"coa": "Course Of Action",
        //"act": "Threat Actor",
        //"cam": "Campaign",
        //"inc": "Incident",
        "tgt": "Exploit Target"
        //"pkg": "Package"
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
        constructor: function () {
            this.duplicates = ko.observable({});
            this.selectedType = ko.observable(null).extend(rate_limited);
            this.originalsLabel = ko.observable("Original");
            this.selectedOriginalId = ko.observable(null).extend(rate_limited);
            this.selectedOriginal = ko.observable(null);
            this.duplicatesLabel = ko.observable("Duplicate");
            this.selectedDuplicateId = ko.observable(null).extend(rate_limited);
            this.selectedDuplicate = ko.observable(null);
            this.analysisStatus = ko.observable(0);
            this.analysisOriginal = ko.observableArray([]);
            this.analysisDuplicate = ko.observableArray([]);
            this.analysisMerge = ko.observable(null);
            this.analysisText = ko.observable("");
            this.searching = ko.observable(true);
            this.localNamespace = ko.observable(false);

            this.typesWithDuplicates = ko.computed(function () {
                var typesWithDuplicates = [];
                var duplicates = this.duplicates();
                ko.utils.objectForEach(type_labels, function (type, label) {
                    var value = duplicates[type] || {};
                    var numDups = Object.keys(value).length;
                    if (numDups > 0) {
                        typesWithDuplicates.push({type: type, label: buildLabel(label, "", numDups)});
                    }
                });
                if (typesWithDuplicates.length > 0) {
                    this.selectedType(typesWithDuplicates[0].type);
                }
                else {
                    typesWithDuplicates.push({type: '', label: buildLabel('No Duplicates Found', "", 0)});
                    this.selectedType(typesWithDuplicates[0].type);
                }
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

            this.allOriginalsAllDuplicatesForType = ko.computed(function() {
                var selectedType = this.selectedType();
                var duplicates = this.duplicates();
                return selectedType && duplicates ? duplicates[selectedType] : {};
            }, this);

            this.selectedOriginalId.subscribe(this._onOriginalChanged, this);
            this.selectedDuplicateId.subscribe(this._onDuplicateChanged, this);
            this.localNamespace.subscribe(function(){
                this.loadDuplicates();
            }, this);
        },

        loadDuplicates: function () {
            this.searching(false);
            var types = Object.keys(type_labels);
            var allDuplicates = {};
            var numLoading = types.length;
            ko.utils.arrayForEach(types, function (type) {
                _postJSON("/adapter/certuk_mod/duplicates/" + type, this.localNamespace(), function (data) {
                    this._onDuplicateLoaded(allDuplicates, data, --numLoading);
                }.bind(this), function (error) {
                    console.error(error);
                    this._onDuplicateLoaded(allDuplicates, null, --numLoading);
                }.bind(this));
            }.bind(this));
        },

        _onDuplicateLoaded: function (allDuplicates, duplicate, numLoading) {
            ko.utils.extend(allDuplicates, duplicate);
            if (numLoading === 0) {
                this._onDuplicatesLoaded(allDuplicates);
            }
        },

        _onDuplicatesLoaded: function (duplicates) {
            this.searching(false);
            this.duplicates(duplicates);
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
            this.analysisStatus(0);
            if (typeof newId === "string") {
                getJSON("/adapter/certuk_mod/duplicates/object/" + newId, null, function (data) {
                    this.selectedDuplicate(new StixPackage(data["package"], data["root_id"]));
                    this.analysisStatus(1);
                }.bind(this));
            } else {
                this.selectedDuplicate(null);
            }
        },

        analyse: function () {
            var data = {
                duplicate: [this.selectedDuplicateId()],
                original: this.selectedOriginalId()
            };
            this.analysisText('Analysing');
            this.analysisStatus(2);
            _postJSON("/adapter/certuk_mod/duplicates/parents/", data, function (data) {
                this._onAnalyse(data);
                this.analysisStatus(3);
            }.bind(this), function (error) {
                this.analysis(error);
                this.analysisStatus(5);
            }.bind(this));
        },

        _onAnalyse: function(data) {
            this.analysisOriginal([]);
            this.analysisDuplicate([]);
            ko.utils.objectForEach(data, function (type, ids) {
                if (type == 'original') {
                    ko.utils.arrayForEach(ids, function (id) {
                        this.analysisOriginal.push(id);
                    }.bind(this))
                }
                else if (type == 'duplicate') {
                    ko.utils.arrayForEach(ids, function (id) {
                        this.analysisDuplicate.push(id)
                    }.bind(this))
                }
            }.bind(this));
        },

        merge: function() {
            var data = {
                duplicate: this.duplicatesForOriginal(),
                original: this.selectedOriginalId(),
                type: this.selectedType()
            };
            this.analysisText('Merging');
            this.analysisStatus(2);
            _postJSON("/adapter/certuk_mod/duplicates/merge/", data, function(data) {
                this.analysisMerge(data);
                this.analysisStatus(4);
            }.bind(this), function(error) {
                this.analysis(error);
                this.analysisStatus(5);
            }.bind(this));
        },

        mergeAll: function() {
            this.analysisText('Merging all Duplicates to Originals');
            this.analysisStatus(2);
            var data = {
                objects: this.allOriginalsAllDuplicatesForType(),
                type: this.selectedType()
            };
            _postJSON("/adapter/certuk_mod/duplicates/merge_all/", data, function (data) {
                this.analysisMerge(data);
                this.analysisStatus(4);
            }.bind(this), function (error) {
                this.analysisMerge(error);
                this.analysisStatus(5);
            }.bind(this))
        }
    });
});
