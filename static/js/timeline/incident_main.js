require([
    "timeline/timeline",
    "common/modal/show-error-modal",
    "common/window-shim",
    "domReady!"
], function (TimeLine, showErrorModal, window) {
    "use strict";
    try {
        (new TimeLine().create_timeline("incidentTimelineSVG", window.rootId, "/adapter/certuk_mod/ajax/incident_timeline/"));
    } catch (e) {
       showErrorModal(e.message, false);
    }
});
