define([
    "dcl/dcl",
    "knockout",
    "common/jquery-shim",
    "common/modal/show-error-modal"
], function (declare, ko, $, showErrorModal) {
    "use strict";

    return declare(null, {
        declaredClass: "ExtractUploadModel",
        constructor: function () {
            this.fileName = ko.observable("");
            this.loading = ko.observable(false);
            this.uploadedId = ko.observable("");
            this.waitIntervalId = ko.observable("");

            this.submitEnabled = ko.computed(function () {
                return this.fileName() != '' && !this.loading();
            }, this);

            this.loading.subscribe(function (isLoading) {
                document.getElementById("_loading_").style.display = isLoading ? null : "none";
            });
        },
        onFileSelected: function (data, event) {
            this.fileName(event.target.files[0].name);
        },
        submitted: function (data, event) {
            this.loading(true);
            var that = this;
            $.ajax({
                url: "/adapter/certuk_mod/extract_upload/",
                type: 'POST',
                data: new FormData($('#extract_upload_form').get(0)),
                cache: false,
                processData: false,
                contentType: false,
                enctype: "multipart/form-data",
                success: function (data) {
                    that.uploadedId(data['result']);
                    that.waitIntervalId(setInterval(that.retrieve.bind(that), 5000));
                },
                error: function (data) {
                    that.uploadedId(data['result']);
                    that.waitIntervalId(setInterval(that.retrieve.bind(that), 5000));
                }
            })

            return false;
        },
        retrieve: function () {
            _ajaxJSON('POST', '/adapter/certuk_mod/ajax/extract_status/', this.uploadedId(),
                function (data) {
                    if (data['result']['state'] === 'COMPLETE') {
                        window.location.href = data['result']['visualiser_url'];
                    } else if (data['result']['state'] === 'FAILED') {
                        clearInterval(this.waitIntervalId());
                        this.loading(false);
                        showErrorModal(data['result']['message'], false);
                    }
                }.bind(this),
                function (data) {
                    clearInterval(this.waitIntervalId());
                    this.loading(false);
                    showErrorModal(data.responseText, false);
                }.bind(this))
        }
    });
});
