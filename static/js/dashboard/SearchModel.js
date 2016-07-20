define([
    "dcl/dcl",
    "knockout",
    "common/window-shim"
], function (declare, ko, window) {
    "use strict";

    var defaultSearchText = "after:16/04/2016 before:26/04/2016 match:stixtype:=:obs match:namespace:=:certuk";
    var mockResults = Object.freeze([
        [(new Date(2016, 3, 26)).toLocaleDateString(), "obs", "Crouching_Powerpoint_Hidden_Trojan_24C3.pdf", "certuk", "WHITE"],
        [(new Date(2016, 3, 25)).toLocaleDateString(), "obs", "Beijings-rising-hackers.pdf", "certuk", "WHITE"],
        [(new Date(2016, 3, 24)).toLocaleDateString(), "obs", "Exile.doc", "certuk", "WHITE"],
        [(new Date(2016, 3, 23)).toLocaleDateString(), "obs", "Deibert.pdf", "certuk", "WHITE"],
        [(new Date(2016, 3, 22)).toLocaleDateString(), "obs", "lingshui.htm", "certuk", "WHITE"],
        [(new Date(2016, 3, 21)).toLocaleDateString(), "obs", "diary.html", "certuk", "WHITE"],
        [(new Date(2016, 3, 20)).toLocaleDateString(), "obs", "government-and.html", "certuk", "WHITE"],
        [(new Date(2016, 3, 19)).toLocaleDateString(), "obs", "AR2008032102605.html", "certuk", "WHITE"],
        [(new Date(2016, 3, 18)).toLocaleDateString(), "obs", "bg_2106.pdf", "certuk", "WHITE"],
        [(new Date(2016, 3, 17)).toLocaleDateString(), "obs", "zeus-crimeware-kit-gets-carding-layout.html", "certuk", "WHITE"],
        [(new Date(2016, 3, 16)).toLocaleDateString(), "obs", "msg00086.html", "certuk", "WHITE"],
    ]);

    return declare(null, {
        declaredClass: "SearchModel",
        constructor: function () {
            var user = window.user;
            var secret = window.secret;
            this.searchText = ko.observable(defaultSearchText);
            this.columns = ko.observableArray([
                "_id", "_source.data.summary.type", "_source.data.summary.title"
            ]);
            this.rowdata = ko.observableArray([]);
            var url = window.location.href
            this.base_url = "http://" + user + ":" + secret + "@" + url.split(":")[1].slice(2) + ":9200/inbox/_search?q=";
            //this.base_url = "http:" + url.split(":")[1] + ":9200/inbox/_search?q=";
        },
        index: function (obj, i) {
            return obj[i];
        },

        get_index: function (params, obj) {
            return params.split('.').reduce(this.index, obj)
        },
        clearSearch: function () {
            this.searchText("");
            this.rowdata([]);
        },
        loadLog: function () {
            var that = this;

            $.ajax({
                url: encodeURI(this.base_url+ this.searchText()),
                data: {},
                type: 'POST',
                dataType: 'application/json',
                contentType:'json',
                withCredentials: true,
                success: function (response) {
                    that.rowdata(JSON.parse(response.responseText).hits.hits);
                },
                beforeSend: function (xhr) {
                    xhr.setRequestHeader('Authorization', 'Basic ' + btoa("es_admin:HelloWorld"));
                },
                error: function (response) {  //why is a success now coming into error!    http.cors.allow-headers?!?
                   that.rowdata(JSON.parse(response.responseText).hits.hits);
                }
            });


        }
    });
});
