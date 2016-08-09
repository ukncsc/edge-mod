define([
    "dcl/dcl",
    "common/modal/Modal",
    "config/PublisherConfig",
    "config/RetentionConfig",
    "config/FTSConfig",
    "config/DeDupConfig",
    "config/CRMConfig",
    "config/HandlingConfig",
    "config/BacklinkConfig"
], function (declare, Modal, PublisherConfig, RetentionConfig, FTSConfig, CRMConfig, HandlingConfig, BacklinkConfig) {
    "use strict";

    return declare(null, {
        declaredClass: "ConfigModel",
        constructor: function () {
            this.publisher = new PublisherConfig();
            this.retention = new RetentionConfig();
            this.fts = new FTSConfig();
            this.dedup = new DeDupConfig();
            this.bl = new BacklinkConfig();
            this.crm = new CRMConfig();
            this.handling = new HandlingConfig();

            this.publisher.getSites();
            this.retention.getConfig();
            this.fts.getConfig();
            this.dedup.getConfig();
            this.crm.getURL();
            this.handling.getConfig();
        }
    });
});
