define([
    "dcl/dcl",
    "common/modal/Modal",
    "config/PublisherConfig",
    "config/RetentionConfig",
    "config/FTSConfig",
    "config/CRMConfig"
], function (declare, Modal, PublisherConfig, RetentionConfig, FTSConfig, CRMConfig) {
    "use strict";

    return declare(null, {
        declaredClass: "ConfigModel",
        constructor: function () {
            this.publisher = new PublisherConfig();
            this.retention = new RetentionConfig();
            this.fts = new FTSConfig();
            this.crm = new CRMConfig();

            this.publisher.getSites();
            this.retention.getConfig();
            this.fts.getConfig();
            this.crm.getURL();
        }
    });
});
