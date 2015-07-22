define(["knockout-3.1.0", "dcl/dcl"], function (ko, declare) {
    return declare(null, {
        constructor: function () {
            this.search = ko.observable("");
            this.results = ko.observableArray([]);
            this.hasResults = ko.computed(function () {
                return this.results().length > 0;
            }, this);
            this.selectedId = ko.observable("");
            this.selectedIncident = ko.observable(null);

            this.search.subscribe(this._onSearchChanged, this);
            this.selectedId.subscribe(this._onSelectionChanged, this);

            this._onSearchChanged(this.search());
        },

        _onSearchChanged: function (/*String*/ newValue) {
            postJSON("/catalog/ajax/load_catalog/", {
                search: newValue,
                size: 10,
                type: "inc"
            }, this._onSearchResponseReceived.bind(this));
        },

        _onSearchResponseReceived: function (response) {
            if (response["success"]) {
                this.results(response["data"]);
            } else {
                alert(response["message"]);
            }
        },

        select: function (incident) {
            this.selectedId(incident.id);
        },

        _onSelectionChanged: function (newId) {
            console.log("Selected:", newId);
            postJSON("/catalog/ajax/get_object/", {
                id: newId
            }, this._onSelectionResponseReceived.bind(this));
        },

        _onSelectionResponseReceived: function (response) {
            if (response["success"]) {
                this.selectedIncident(response);
            } else {
                alert(response["message"]);
            }
        }
    });
});
