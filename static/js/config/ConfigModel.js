define([
    "dcl/dcl",
    "common/modal/Modal",
    "config/PublisherConfig",
    "config/RetentionConfig",
    "config/CRMConfig"
], function (declare, Modal, PublisherConfig, RetentionConfig, CRMConfig) {
    "use strict";

    return declare(null, {
        declaredClass: "ConfigModel",
        constructor: function () {
            this.publisher = new PublisherConfig();
            this.retention = new RetentionConfig();
            this.crm = new CRMConfig();

            this.publisher.getSites();
            this.retention.getConfig();
            this.crm.getURL();
        }
    });
});
