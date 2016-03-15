define([
    "common/window-shim"
], function (window) {
    "use strict";

    return function (id) {

        var params = {'id': id};
        postJSON(window.ajax_uri + 'load_draft/', params, function (response) {
            if (response['success']) {
                window.vm.populateGuiFomJson(response['draft']);
                window.vm.tracker().markCurrentStateAsClean();
            } else {
                alert(response['message']);
            }
        })
    };
});
