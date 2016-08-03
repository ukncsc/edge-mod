define([
    "dcl/dcl",
    "common/modal/Modal",
    "config/PublisherConfig",
    "config/RetentionConfig",
    "config/FTSConfig",
    "config/CRMConfig",
    "config/HandlingConfig",
    "config/MarkingConfig"
], function (declare, Modal, PublisherConfig, RetentionConfig, FTSConfig, CRMConfig, HandlingConfig, MarkingConfig) {
    "use strict";

    return declare(null, {
        declaredClass: "ConfigModel",
        constructor: function () {
            this.publisher = new PublisherConfig();
            this.retention = new RetentionConfig();
            this.fts = new FTSConfig();
            this.crm = new CRMConfig();
            this.handling = new HandlingConfig();
            this.markings = new MarkingConfig();

            this.publisher.getSites();
            this.retention.getConfig();
            this.fts.getConfig();
            this.crm.getURL();
            this.handling.getConfig();
            this.markings.getConfig();
        }
    });
});
