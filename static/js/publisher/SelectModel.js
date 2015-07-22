define(["knockout-3.1.0", "dcl/dcl"], function (ko, declare) {
    return declare(null, {
        constructor: function () {
            this.search = ko.observable("");
            this.results = ko.observableArray([]);
            this.hasResults = ko.computed(function () {
                return this.results().length > 0;
            }, this);

            this.search.subscribe(this._onSearchChanged, this);
            this._onSearchChanged(this.search());
        },

        _onSearchChanged: function (/*String*/ newValue) {
            postJSON("/catalog/ajax/load_catalog/", {
                search: newValue,
                size: 10,
                type: "inc"
            }, this._onResponseReceived.bind(this));
        },

        _onResponseReceived: function (response) {
            if (response["success"]) {
                this._onSearchResultsObtained(response["data"]);
            } else {
                alert(response["message"]);
            }
        },

        _onSearchResultsObtained: function (results) {
            this.results(results);
        }
    });
});
