define(["../../../../dcl/dcl",
        "knockout",
        "ind-build/indicator-builder-shim",
        "ind-build/tests/unit/mock/mock-messages"],
    function (declare, ko, indicator_builder, Messages) {
        var MOCKObservable = declare(null, {

            constructor: function () {
                this.hashes = ko.observableArray([]);

                this.selected_hash = ko.observable("");
                this.hash_value = ko.observable("");
                this.objectTitle = ko.observable("");
                this.objectType = ko.observable("File");
                this.file_name = ko.observable("");
                this.file_extension = ko.observable("")
            },
            doValidation: function () {
                return new Messages();
            },
            removeHash: function (hash) {
                this.hashes.remove(hash);
            },
            getSearchValue: function (hash) {
            },
            load: function (hash) {
            },
            addHash: function (file) {
            },
            save: function () {
                return ko.toJSON(this);
            }
        });

        indicator_builder.ObservableFile = MOCKObservable;

        return MOCKObservable;
    });
