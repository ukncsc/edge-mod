define([
    "knockout",
    "./Modal",
    "kotemplate!modal-error-content:common/modal/templates/error-modal-content.html"
], function (ko, Modal, errorContentTemplate) {
    "use strict";

    return function (title, content, show_back) {
        var publishModal = new Modal({
            title: title,
            titleIcon: "glyphicon-ok-sign",
            contentData: content,
            contentTemplate: errorContentTemplate.id,
            width: "90%"
        });
        if (show_back) {
            publishModal.getButtonByLabel("OK").callback = history.back.bind(history);
        }
        publishModal.show();
    };
});

