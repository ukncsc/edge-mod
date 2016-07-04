define([
    "dcl/dcl",
    "knockout"
], function (declare,ko) {
    "use strict";

    return declare(null, {
        declaredClass: "ExtractStatusModel",
        constructor: function () {
            this.results = ko.observableArray([]);
            setInterval(this.retrieve.bind(this), 5000);
            this.retrieve();
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
