define([
    "dcl/dcl",
    "knockout"
], function (declare,ko) {
    "use strict";

    return declare(null, {
        declaredClass: "ExtractUploadModel",
        constructor: function () {
            this.results = ko.observableArray([]);
            this.exists = ko.observable(false);
            this.fileName = ko.observable("");

            this.alreadySubmitted = ko.observable(false);

            this.submitEnabled = ko.computed(function () {
                return this.exists() && !this.alreadySubmitted();
            }, this);

            this.results = ko.observableArray([]);
            setInterval(this.retrieve.bind(this), 5000)
        },
        onFileSelected: function (data, event) {
            this.fileName(event.target.files[0].name);
            this.exists(true);
        },
        submitted: function(data, event) {
            this.alreadySubmitted(true);
            return true;
        },
        retrieve: function() {
            this.alreadySubmitted(false);
            postJSON('/adapter/certuk_mod/ajax/extract_list/', this.results, function(data){
                this.results(data['result'])
            }.bind(this))
        }
    });
});
