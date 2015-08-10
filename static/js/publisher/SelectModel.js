define([
    "knockout",
    "dcl/dcl",
    "stix/StixPackage"
], function (ko, declare, StixPackage) {
    "use strict";

    return declare(null, {
        constructor: function (rootId, stixPackage) {
            this.stixPackage = ko.observable(new StixPackage(stixPackage, rootId));

            this.root = ko.computed(function () {
                return this.stixPackage().root;
            }, this);
            this.type = ko.computed(function () {
                return this.stixPackage().type;
            }, this);
        },

        onPublish: function () {
            if (confirm("Are you absolutely sure you want to publish this package?")) {
                postJSON("/adapter/publisher/ajax/publish/", {
                    root_id: this.root().id()
                }, this._onPublishResponseReceived.bind(this));
            }
        },

        _onPublishResponseReceived: function (response) {
            var message = response["success"] ? "The package was successfully published." : response["error_message"];
            alert(message);
        }
    });
});
