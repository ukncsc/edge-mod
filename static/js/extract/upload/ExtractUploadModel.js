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
            this.submitResetTime = ko.observable(true);
            this.submitEnabled = ko.computed(function () {
                return this.fileName() != '' && this.submitResetTime();
            }, this);

            this.results = ko.observableArray([]);
            setInterval(this.retrieve.bind(this), 5000);
            this.retrieve();
        },
        onFileSelected: function (data, event) {
            this.fileName(event.target.files[0].name);
        },
        submitted: function(data, event) {
            this.fileName('');
            this.submitResetTime(false)
            //The following line prevents submitting frequently. Not great, would rather submit in JS and handle result.
            var si = setInterval(
                function() {
                        this.submitResetTime(true);
                        clearInterval(si)
                    }.bind(this), 15000);
            return true;
        },
        retrieve: function() {
            postJSON('/adapter/certuk_mod/ajax/extract_list/', this.results, function(data){
                this.results(data['result'])
            }.bind(this))
        },
        deleteExtract: function(that, model){
            postJSON('/adapter/certuk_mod/ajax/delete_extract/', model['id'], function(data){
                that.retrieve()
            }.bind(that));
        }
    });
});
