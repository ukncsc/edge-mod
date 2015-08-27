define([
    "dcl/dcl",
    "knockout",
    "kotemplate!modal-container:./modal-template.html",
    "kotemplate!modal-default-content:./text-content.html"
], function (declare, ko, modalContainerTemplate, defaultContentTemplate) {
    "use strict";

    return declare(null, {
        constructor: function (options) {
            this.title = ko.observable(options["title"]);
            this.titleIcon = ko.observable(options["titleIcon"]);

            this.contentTemplate = options["contentTemplate"] || defaultContentTemplate.id;
            this.contentData = options["contentData"]; // No default view-model, let the bindings fail instead...

            this.buttonData = ko.observableArray(options["buttonData"] || [
                    {
                        label: "OK"
                    }
                ]);

            this.width = options["width"];
            this.height = options["height"];

            this.modalReference = null;

            this.onShow = options["onShow"];
        },

        show: function () {
            if (this.modalReference !== null) {
                console.log("Attempt to show modal (title: " + this.title() + ") that is already open.");
                this.modalReference.modal("hide");
                this.modalReference = null;
            }

            var targetDiv = document.createElement("div");
            targetDiv.style.display = "none";
            document.body.appendChild(targetDiv);

            var afterRender = this._afterModalRender.bind(this);

            ko.renderTemplate(
                modalContainerTemplate.id,
                this,
                {
                    afterRender: afterRender
                },
                targetDiv,
                "replaceNode"
            );
        },

        _afterModalRender: function (nodes) {
            // Get the modal:
            var modalElements = nodes.filter(function(node) {
                return node.nodeType === 1; // Ignore text
            });
            var modal = $(modalElements);

            // Ensure it always removes itself from the DOM when closed, and clean up the KO bindings:
            modal.on("hidden.bs.modal", function () {
                modal.each(function (index, element) { ko.cleanNode(element); });
                modal.remove();
            });

            // Show it:
            modal.modal({
                backdrop: "static",
                keyboard: false,
                width: this.width,
                height: this.height
            });

            this.modalReference = modal;

            if (this.onShow) {
                this.onShow(this);
            }
        },

        handleClick: function (button) {
            if (typeof button.callback === "function") {
                button.callback(this);
            }
            if (button.noClose !== true) {
                this.modalReference.modal("hide");
                this.modalReference = null;
            }
        },

        getButtonByLabel: function (label) {
            if (typeof label !== "string") {
                throw new TypeError("Label must be of string type and cannot be null.");
            }

            var button = ko.utils.arrayFirst(this.buttonData(), function (item) {
                return item.label === label;
            }, this);

            if (!button) {
                throw new Error("A button with label='" + label + "' was not found.")
            }

            return button;
        }
    });
});
