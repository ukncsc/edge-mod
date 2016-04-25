define([
    "knockout",
    "./Modal",
    "kotemplate!modal-error-content:common/modal/templates/error-modal-content.html",
], function (ko, Modal, errorContentTemplate) {
    "use strict";

    return function (content, show_back) {
        var errorModal = new Modal({
            title: "Error",
            titleIcon: "glyphicon-warning-sign",
            contentData: content,
            contentTemplate: errorContentTemplate.id,
            width: "90%"
        });
        if (show_back) {
            errorModal.getButtonByLabel("OK").callback = history.back.bind(history);
        }
        errorModal.show();
    };
});

