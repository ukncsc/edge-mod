require([
    "timeline/timeline",
    "common/modal/Modal",
    "kotemplate!modal-error-content:publisher/templates/error-modal-content.html",
    "common/window-shim",
    "domReady!"
], function (TimeLine, Modal, errorContentTemplate, window) {
    "use strict";
    try {
        (new TimeLine().create_timeline("incidentTimelineSVG", window.rootId, "/adapter/certuk_mod/ajax/incident_timeline/"));
    } catch (e) {
        // Post merge with #109 into develop, change to use show-error-modal
        var errorModal = new Modal({
            title: "Error",
            titleIcon: "glyphicon-warning-sign",
            contentData: e.message,
            contentTemplate: errorContentTemplate.id,
            width: "90%"
        });

        errorModal.show();
    }
});
