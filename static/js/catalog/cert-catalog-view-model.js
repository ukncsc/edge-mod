define([
    "dcl/dcl",
    "knockout",
    "common/modal/Modal",
    "stix/StixPackage",
    "catalog/cert-catalog-build-section",
    "common/topic",
    "catalog/cert-catalog-topics",
    "catalog/cert-catalog-handling",
    "common/modal/show-error-modal",
    "text!config-service",
    "kotemplate!publish-modal:./templates/publish-modal-content.html",
    "kotemplate!validation-results:./templates/validation-results.html"
], function (declare, ko, Modal, StixPackage, Section, Topic, topics, Handling, showErrorModal, configService, publishModalTemplate) {
    "use strict";

    var handlingEnabled = false

    var config = Object.freeze(JSON.parse(configService));
    var handling = config.sharing_groups;
    if (handling) {
        handlingEnabled = handling.enabled;
    }

    return declare(null, {
        constructor: function (rootId, stixPackage, trustGroups, validationInfo, viewURL, editURL, edges) {
            this.stixPackage = ko.observable(new StixPackage(stixPackage, rootId, trustGroups, validationInfo, edges));

            this.root = ko.computed(function () {
                return this.stixPackage().root;
            }, this);
            this.type = ko.computed(function () {
                return this.stixPackage().type;
            }, this);
            this.viewURL = ko.observable(viewURL);
            this.editURL = ko.observable(editURL);
            this.rootID = ko.observable(rootId);
            this.revision = ko.observable("");
            this.sightings = ko.observable("");
            this.editable = ko.observable(this.isEditable(rootId))
            this.section = ko.observable(new Section());
            this.handlingEnabled = ko.observable(handlingEnabled);
            this.handling = ko.observable(new Handling());
            this.extractHandler = this.extractObservable.bind(this);
            Topic.subscribe(topics.HANDLING, function () {
                this.externalPublish()
            }.bind(this), this);
            Topic.subscribe(topics.REVISION, function (data) {
                this.reload(data)
            }.bind(this), this);
            this.extractablesInPlainText = ko.observableArray([
                new this.stixObservableType("All", "all", "text"),
                new this.stixObservableType("Http Session", "HTTPSessionObjectType", "text"),
                new this.stixObservableType("Network Connection", "NetworkConnectionObjectType", "text"),
                new this.stixObservableType("Address", "AddressObjectType", "text"),
                new this.stixObservableType("URI", "URIObjectType", "text"),
                new this.stixObservableType("Hostname", "HostnameObjectType", "text"),
                new this.stixObservableType("Domain", "DomainNameObjectType", "text"),
                new this.stixObservableType("Mutex", "MutexObjectType", "text"),
                new this.stixObservableType("File", "FileObjectType", "text"),
                new this.stixObservableType("Socket", "SocketAddressObjectType", "text"),
                new this.stixObservableType("Registery Key", "WindowsRegistryKeyObjectType", "text"),
                new this.stixObservableType("Artifact", "ArtifactObjectType", "text"),
                new this.stixObservableType("Email", "EmailMessageObjectType", "text")
            ]);
            this.extractablesInSnort = ko.observableArray([
                new this.stixObservableType("All", "all", "SNORT"),
                new this.stixObservableType("Domain", "DomainNameObjectType", "SNORT"),
                new this.stixObservableType("Address", "AddressObjectType", "SNORT")
            ]);
        },
       stixObservableType : function (name, path, type) {
            this.name = name;
            this.path = path;
            this.type = type;
        },
        extractObservable: function (stixObservableType) {
            var href = encodeURI("/adapter/certuk_mod/observable_extract/" + stixObservableType.type +"/" + stixObservableType.path + "/" + this.rootID() + '/' + this.revision());
            var successHandler = function (response) {
                var data = JSON.parse(response)
                if (data["observables-found"])
                    window.location.href = href + "/download";
                else
                {
                    if (stixObservableType.name == "All")
                        showErrorModal("There are no observables to download")
                    else
                        showErrorModal("There are no observables of type: " + stixObservableType.name)
                }
            }
            var failureHandler = function () {
                    showErrorModal("An error occurred whilst attempting to download Observables")
            }
            getJSON(href, null, successHandler, failureHandler)

            return false
        },
        reload: function (timekey) {
            if (timekey !== this.revision()) {
                var params = {"id": this.rootID(), "revision": timekey}
                postJSON("/adapter/certuk_mod/reload/", params, function (response) {
                    this.stixPackage(new StixPackage(response["package"], this.rootID(), JSON.parse(response["trust_groups"]), JSON.parse(response["validation_info"]), response["edges"]))
                    this.revision(response["revision"])
                }.bind(this));
            }
        },

        isEditable: function (id) {
            postJSON("/adapter/certuk_mod/review/editable/" + id, "", function (response) {
                this.editable(response["allow_edit"]);
            }.bind(this));
        },

        loadStatic: function (optionsList) {
            this.sightings(optionsList.sightings);
            this.revision(optionsList.revision);
            this.handling().loadStatic(optionsList.handlingCaveats);
            this.section().loadStatic(optionsList);
        },

        _onPublishModalOK: function (modal) {
            var yesButton = modal.getButtonByLabel("Yes");
            var noButton = modal.getButtonByLabel("No");
            var closeButton = modal.getButtonByLabel("Close");

            yesButton.disabled(true);
            noButton.disabled(true);

            modal.contentData.waitingForResponse(true);
            modal.contentData.message("Publishing...");

            this.publish({
                'publicationMessage': modal.contentData.publicationMessage()
            }, function (response) {
                modal.contentData.phase("RESPONSE");
                modal.contentData.waitingForResponse(false);

                var success = !!(response["success"]);
                var errorMessage = response["error_message"];
                if (errorMessage) {
                    errorMessage = errorMessage.replace(/^[A-Z]/, function (match) {
                        return match.toLowerCase();
                    }).replace(/[,.]+$/, "");
                }
                var message = success ?
                    "The package was successfully published." :
                "An error occurred during publish (" + errorMessage + ")";
                var title = success ? "Success" : "Error";
                var titleIcon = success ? "glyphicon-ok-sign" : "glyphicon-exclamation-sign";

                modal.title(title);
                modal.titleIcon(titleIcon);
                modal.contentData.message(message);

                yesButton.hide(true);
                noButton.hide(true);
                closeButton.hide(false);
            }.bind(this));
        },

        onPublish: function () {
            //Can't set handling on observables as they are CYBOX Objects not STIX
            //therefore go straight to externalPublish
            if (!this.handlingEnabled() || this.type().code === "obs") {
                this.externalPublish()
            } else {
                this.handling().onPublish(this.externalPublish);
            }
        },

        _onCloseCallback: function () {
            this.reload("latest");
        },

        externalPublish: function () {
            var validations = this.stixPackage().validations();
            var contentData = {
                phase: ko.observable("INPUT"),
                message: ko.observable("Are you absolutely sure you want to publish this package?"),
                messageWarning: "This package has warnings. If you wish to proceed, please describe below why you believe the warnings are not relevant in this case",
                messageError: "This package has errors and cannot be published",
                validations: validations,
                publicationMessage: ko.observable(""),
                waitingForResponse: ko.observable(false)
            };

            var hasErrors = validations.hasErrors();
            var confirmModal = new Modal({
                title: hasErrors ? "Error" : "Warning",
                titleIcon: hasErrors ? "glyphicon-ban-circle" : "glyphicon-exclamation-sign",
                contentData: contentData,
                contentTemplate: publishModalTemplate.id,
                buttonData: [
                    {
                        label: "Yes",
                        noClose: true,
                        callback: this._onPublishModalOK.bind(this),
                        disabled: ko.observable(false),
                        icon: "glyphicon-ok",
                        hide: ko.observable(false)
                    },
                    {
                        label: "No",
                        icon: "glyphicon-remove",
                        disabled: ko.observable(false),
                        hide: ko.observable(false)
                    },
                    {
                        label: "Close",
                        hide: ko.observable(true)
                    }
                ],
                onCloseCallback: this._onCloseCallback.bind(this)
            });

            if (hasErrors) {
                confirmModal.getButtonByLabel("Yes").hide(true);
                confirmModal.getButtonByLabel("No").hide(true);
                confirmModal.getButtonByLabel("Close").hide(false);
            } else if (validations.hasWarnings()) {
                var publicationMessage = contentData.publicationMessage;
                publicationMessage.subscribe(function (newValue) {
                    var hasMessage = (typeof newValue === "string" && newValue.length > 0);
                    confirmModal.getButtonByLabel("Yes").disabled(!hasMessage);
                });
                publicationMessage.valueHasMutated();
            }
            confirmModal.show();
        },

        publish: function (onConfirmData, onPublishCallback) {
            postJSON("/adapter/certuk_mod/ajax/publish/", ko.utils.extend(onConfirmData, {
                root_id: this.root().id()
            }), onPublishCallback);
        },

        onRowClicked: function (item, event) {
            if (item.id() && item.title().value() != "(External)") {
                window.open("/object/" + item.id());
            }
        }
    });
});
