define([
    "dcl/dcl",
    "knockout",
    "inc-build/cert-incident-builder-shim",
    "common/cert-build-mode",
    "inc-build/cert-inc-build-section",
    "common/cert-build-functions",
], function (declare, ko, incident_builder, BuildMode, Section, buildFunctions) {
    "use strict";

    function ViewModel() {
        this.id = ko.observable();
        this.id_ns = ko.observable();
        this.mode = ko.observable(new BuildMode());
        this.section = ko.observable(new Section());
        this.compositionType = ko.observable("OR");

        this.ko_view_url = ko.observable();
        this.ko_edit_url = ko.observable();
        this.ko_detail_url = ko.observable();

        this.draft_list = ko.observableArray([]);
        this.draft_selected = ko.observable();
        this.messages = ko.computed(function () {
            return this.section().doValidation();
        }, this);
        this.ct = this.changeTracker();
    }

    function buildRestUrl(/*String*/ path) {
        return incident_builder["ajax_uri"] + path + "/";
    }

    function loadFromServer(context, path, id, dataItemName) {
        postJSON(buildRestUrl(path), {
            id: id
        }, function (response) {
            if (response["success"]) {
                this.id(response[dataItemName]["id"]);
                this.id_ns(response[dataItemName]["id_ns"]);
                this.ko_view_url(response[dataItemName]["view_url"]);
                this.ko_edit_url(response[dataItemName]["edit_url"]);
                this.ko_detail_url(response[dataItemName]["detail_url"]);
                this.compositionType(response[dataItemName]["composition_type"] || "OR");
                this.section().load(response[dataItemName]);
                this.tracker().markCurrentStateAsClean();
            } else {
                alert(response["message"]);
            }
        }.bind(context));
    }

    ViewModel.prototype = {
        constructor: ViewModel,

        loadStatic: function (optionLists) {
            this.section().loadStatic(optionLists);
        },

        initDraft: function (default_tlp, default_producer) {
            postJSON(buildRestUrl("get_new_id"), null, function (response) {
                if (response["success"]) {
                    this.id(response["id"]);
                    this.section().load({
                        tlp: default_tlp,
                        producer: default_producer
                    });
                    this.tracker().markCurrentStateAsClean();
                } else {
                    alert(response["message"]);
                }
            }.bind(this));
        },

        openDraftList: function () {
            postJSON(buildRestUrl("load_draft_list"), {}, function (d) {
                this.draft_list.removeAll();
                if ($.inArray("drafts", d)) {
                    $.each(d["drafts"], function (i, v) {
                        this.draft_list.push({
                            id: v["draft"]["id"],
                            title: v["draft"]["title"]
                        });
                    }.bind(this));
                    $("#draft_list").show();
                }
            }.bind(this));
        },

        loadDraftFromList: function () {
            if (this.draft_selected().id.length > 0) {
                this.loadDraft(this.draft_selected().id);
            }
            this.closeDraftList();
            this.section().select(this.section().findByLabel("General")());
        },

        closeDraftList: function () {
            $("#draft_list").hide()
        },

        loadDraft: function (id) {
            loadFromServer(this, "load_draft", id, "draft");
        },

        saveDraft: function () {
            var msgs = this.section().doValidation();
            if (msgs.hasErrors()) {
                alert(msgs.errors.peek().join("\n"));
            } else {
                var data = this.section().save();
                data.id = this.id();
                data.id_ns = this.id_ns();
                data.composition_type = this.compositionType();
                postJSON(buildRestUrl("save_draft"), data, function (response) {
                    if (response["success"]) {
                        this.tracker().markCurrentStateAsClean();
                    } else {
                        alert(response["message"]);
                    }
                }.bind(this));
            }
        },

        deleteDraft: function () {
            if (confirm("Are you sure you want to delete draft " + this.id() + "?")) {
                postJSON(buildRestUrl("delete_draft"), {
                    id: this.id()
                }, function (response) {
                    if (response["success"]) {
                        this.initDraft();
                    } else {
                        alert(response["message"]);
                    }
                }.bind(this));
            }
        },

        publish: function () {
            var msgs = this.section().doValidation();
            if (msgs.hasErrors()) {
                alert(msgs.errors.peek().join("\n"));
            } else {
                var data = this.section().save();
                data.id = this.id();
                data.id_ns = this.id_ns();
                data.composition_type = this.compositionType();
                postJSON(buildRestUrl("create_incident"), data, function (response) {
                    if (response["success"]) {
                        alert("The incident has been published");
                        window.location.assign(window.location.href.split("/incident/")[0] + "/incident/build/");
                    } else {
                        alert(response["message"]);
                    }
                }.bind(this));
            }
        },

        loadObject: function (id) {
            loadFromServer(this, "load_object", id, "data");
        },

        isIncomplete: function () {
            return this.messages().hasMessages();
        },

        changeTracker :function() {
            return buildFunctions.changeTracker(this.section().options(), function (obj) {
                function stringify(obj) {
                    var type, returned;
                    if (obj === null) return "n";
                    if (obj === true) return "t";
                    if (obj === false) return "f";
                    if (ko.isObservable(obj)) {
                        if (ko.isComputed(obj)) {
                            return null;
                        } else {
                            return stringify(obj());
                        }
                    }
                    if (obj instanceof Function) return null;
                    if (obj instanceof Date) return "d:" + (0 + obj);
                    type = typeof obj;
                    if (type === "string") return "s:" + obj.replace(/([\\;])/g, "\\$1");
                    if (type === "number") return "n:" + obj;
                    if (obj instanceof Array) {
                        return "a:" + ko.utils.arrayMap(obj, function (item) {
                                return stringify(item);
                            }).join(";");
                    }
                    returned = [];
                    ko.utils.objectForEach(obj, function(name, value) {
                        var stringified = stringify(value);
                        if (stringified) {
                            returned.push(name + ":" + stringified);
                        }
                    });
                    return "o:" + returned.join(";");
                }
                return stringify(obj);
            });
        },

        tracker: function () {
            return this.ct();
        }
    };

    return ViewModel;
});
