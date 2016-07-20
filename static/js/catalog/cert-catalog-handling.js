define([
    "dcl/dcl",
    "knockout",
    "common/modal/Modal",
    "kotemplate!list-select:./templates/publish_handling.html",
    "text!config-service"
], function (declare, ko, Modal, ListSelectsTemplate, configService) {
    "use strict";

    var config = Object.freeze(JSON.parse(configService));
    var sharing_groups = config.sharing_groups;

    return declare(null, {
        declaredClass: "cert-catalog-handling",
        constructor: function () {
            this.choices = ko.observableArray(this.parseSharingGroups(sharing_groups))
            this.items = ko.observableArray([]);

        },

        parseSharingGroups: function (sharingGroups) {
            var LabelList = [];
            for (var key in sharingGroups) {
                if (sharingGroups.hasOwnProperty(key)) {
                    LabelList.push(sharingGroups[key])
                }
            }
            return LabelList
        },

        toggle: function (item) {
            if (this.isSelected(item)) {
                this.items.remove(item);
            } else {
                this.items.push(item)
            }
        },

        isSelected: function (item) {
            return this.items.indexOf(item) > -1;
        },

        onPublish2: function () {
            var contentData = {
                choices: this.choices()
            };

            var confirmModal = new Modal({
                title: "Handling Caveats",
                titleIcon: "glyphicon-info-sign",
                contentData: contentData,
                contentTemplate: ListSelectsTemplate.id,
                buttonData: [
                    {
                        label: "Yes",
                        noClose: true,
                        //callback: this._onPublishModalOK.bind(this),
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
                ]
            });
            confirmModal.show();
        },
    });
});
