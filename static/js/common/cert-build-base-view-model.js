define([
    "dcl/dcl",
    "knockout",
    "common/modal/Modal",
    "kotemplate!builder-publish:./templates/builder-publish-modal.html",
    "common/cert-build-mode",
    "common/cert-build-functions",
    "stix/ValidationInfo",
    "kotemplate!validation-results:../publisher/templates/validation-results.html",
    "common/modal/publish-modal-content",
    "common/cert-build-base-view-model",
    "common/change-tracker"
], function (declare, ko, Modal, builderPublishModalTemplate, BuildMode, buildFunctions, ValidationInfo, ValidationResults, PublishModalContent, BaseViewModel, ChangeTracker) {
    "use strict";

    var BaseViewModel = declare(null, {
        declaredClass: "BaseViewModel",

        constructor: function (ajax_uri, Section) {
            this.id = ko.observable();
            this.ajax_uri = ko.observable(ajax_uri);
            this.id_ns = ko.observable();
            this.mode = ko.observable(new BuildMode());
            this.section = ko.observable(new Section());

            this.ko_view_url = ko.observable();
            this.ko_edit_url = ko.observable();
            this.ko_detail_url = ko.observable();

            this.draft_list = ko.observableArray([]);
            this.draft_selected = ko.observable();
            this.messages = ko.computed(function () {
                return this.section().doValidation();
            }, this);
            this.ct = ChangeTracker.create(this.section().options());
        },

        buildRestUrl: function (/*String*/ path) {
            return this.ajax_uri() + path + "/";
        },

        loadFromServer: function (path, id, dataItemName) {
            var self = this;
            postJSON(this.buildRestUrl(path), {
                id: id
            }, function (response) {
                if (response["success"]) {
                    self.id(response[dataItemName]["id"]);
                    self.id_ns(response[dataItemName]["id_ns"]);
                    self.ko_view_url(response[dataItemName]["view_url"]);
                    self.ko_edit_url(response[dataItemName]["edit_url"]);
                    self.ko_detail_url(response[dataItemName]["detail_url"]);
                    self.section().load(response[dataItemName]);
                    self.tracker().markCurrentStateAsClean();
                } else {
                    alert(response["message"]);
                }
            });
        },
        loadStatic: function (optionLists) {
            this.section().loadStatic(optionLists);
        },

        initDraft: function (default_tlp, default_producer) {
            postJSON(this.buildRestUrl("get_new_id"), null, function (response) {
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
            postJSON(this.buildRestUrl("load_draft_list"), {}, function (d) {
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

        _serialize: function () {
            var data = this.section().save();
            data.id = this.id();
            data.id_ns = this.id_ns();
            data.stixtype = this.stixtype();

            return data;
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
            this.loadFromServer("load_draft", id, "draft");
        },

        saveDraft: function () {
            var title = ko.unwrap(this.section().findByLabel("General")).title;
            if (title.hasError()) {
                alert("You need to enter a title");
            } else {
                var data = this._serialize();
                postJSON(this.buildRestUrl("save_draft"), data, function (response) {
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
                postJSON(this.buildRestUrl("delete_draft"), {
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

        _constructPublishModalContent: function () {
            return new PublishModalContent();
        },

        getValidationResult: function (data, onResponseCallback) {
            postJSON("/adapter/certuk_mod/ajax/validate/", data, onResponseCallback);
        },

        _validate: function (modal) {
            modal.contentData.waitingForResponse(true);
            modal.contentData.message("Validating...");
            modal.getButtonByLabel("Close").disabled(true);

            var data = this._serialize();

            this.getValidationResult(data, function (response) {
                var rawValidation = response['validation_info'];
                var validations = new ValidationInfo(rawValidation);
                modal.contentData.message("");
                modal.contentData.validations = validations;

                modal.contentData.waitingForResponse(false);
                modal.contentData.responseType("VAL");

                if (!response["success"]) {
                    modal.title("Error");
                    modal.titleIcon("glyphicon-exclamation-sign");
                    modal.contentData.status("FAILED");
                    modal.contentData.message("An error occurred during validation (" + response["error_message"] + ")");
                    modal.getButtonByLabel("Close").disabled(false);
                    return;
                }

                if (validations.hasErrors()) {
                    modal.title("Error");
                    modal.titleIcon("glyphicon-exclamation-sign");
                    modal.contentData.status("ERROR");
                    modal.getButtonByLabel("Close").disabled(false);
                } else if (validations.hasWarnings() || validations.hasInfos()) {
                    modal.getButtonByLabel("Yes").hide(false);
                    modal.getButtonByLabel("No").hide(false);
                    modal.getButtonByLabel("Close").hide(true);
                    modal.contentData.message(this.messageConfirmPublish);
                    if (validations.hasWarnings()) {
                        modal.contentData.status("WARNING");
                    } else {
                        modal.contentData.status("INFO");
                    }
                } else {
                    modal.contentData.status("OK");
                    modal.contentData.message("Validation successful...");
                    setTimeout(function () {
                        this._publish(modal);
                    }.bind(this), this.REDIRECT_DELAY);
                }
            }.bind(this));
        },

        _publish: function (modal) {
            modal.contentData.message("Publishing...");
            modal.contentData.waitingForResponse(true);
            modal.contentData.responseType(null);
            modal.getButtonByLabel("Yes").disabled(true);
            modal.getButtonByLabel("No").disabled(true);
            modal.getButtonByLabel("Close").disabled(true);

            this.getPublishResult(this._serialize(), function (response) {
                modal.contentData.waitingForResponse(false);
                modal.contentData.responseType("PUB");

                modal.getButtonByLabel("Yes").hide(true);
                modal.getButtonByLabel("No").hide(true);
                modal.getButtonByLabel("Close").disabled(false);
                modal.getButtonByLabel("Close").hide(false);

                if (response["success"]) {
                    modal.contentData.status("OK");
                    modal.contentData.message("Successfully published internally");
                    modal.titleIcon("glyphicon-ok-sign");

                    window.location.assign('/object/' + this.id());

                    setTimeout(function () {
                        window.location.assign('/object/' + this.id());
                    }, this.REDIRECT_DELAY);
                } else {
                    modal.contentData.status("FAILED");
                    modal.contentData.message(response["message"]);
                    modal.titleIcon("glyphicon-exclamation-sign");
                }
            }.bind(this));
        },

        getPublishResult: function (data, onResponseCallback) {

        },

        publish: function () {
            var contentData = this._constructPublishModalContent();
            var clientValidation = this.section().doValidation();
            var hasErrors = clientValidation.hasErrors();
            var confirmModal = new Modal({
                title: hasErrors ? "Unable to publish" : "Publish",
                titleIcon: hasErrors ? "glyphicon-ban-circle" : "glyphicon-exclamation-sign",
                contentData: contentData,
                contentTemplate: builderPublishModalTemplate.id,
                buttonData: [
                    {
                        label: "Yes",
                        noClose: true,
                        callback: this._publish.bind(this),
                        icon: "glyphicon-ok",
                        hide: ko.observable(true),
                        disabled: ko.observable(false)
                    },
                    {
                        label: "No",
                        icon: "glyphicon-remove",
                        hide: ko.observable(true),
                        disabled: ko.observable(false)
                    },
                    {
                        label: "Close",
                        hide: ko.observable(false),
                        disabled: ko.observable(false)
                    }
                ]
            });

            confirmModal.show();

            if (hasErrors) {
                contentData.responseType("CLIENT_ERROR");
                contentData.status("ERROR");
                contentData.message("");
                contentData.clientErrors(clientValidation.errors.peek());
            } else {
                this._validate.call(this, confirmModal);
            }
        },

        loadObject: function (id) {
            this.loadFromServer("load_object", id, "data");
        },

        isIncomplete: function () {
            return this.messages().hasMessages();
        },

        tracker: function () {
            return this.ct();
        }
    })
    return BaseViewModel;
})
;