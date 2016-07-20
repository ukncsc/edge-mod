define([
    "dcl/dcl",
    "knockout",
    "jquery",
    "gridster",
    "./Panel",
    "common/window-shim"
], function (declare, ko, $, gridster, Panel, window) {
    "use strict";

    return declare(null, {
        declaredClass: "DashboardModel",
        constructor: function () {
            var user = window.user;
            var secret = window.secret;
            var url = window.location.href
            var domain = url.split(":")[1];

            console.log(domain);
            this.panels = ko.observableArray([
                ko.observable(new Panel(1, 1, 3, 3, "Type by Type", "http://" + "es_admin" + ":" + "HelloWorld" + "@" + domain.slice(2) + ":5601/app/kibana#/visualize/edit/Typesx2?embed=true&_g=(refreshInterval:(display:Off,pause:!f,value:0),time:(from:now-5y,mode:quick,to:now))&_a=(filters:!(),linked:!f,query:(query_string:(analyze_wildcard:!t,query:'*')),uiState:(),vis:(aggs:!((id:'1',params:(),schema:metric,type:count),(id:'2',params:(field:type,order:desc,orderBy:'1',size:5),schema:segment,type:terms),(id:'3',params:(field:data.summary.type,order:desc,orderBy:'1',size:5),schema:segment,type:terms)),listeners:(),params:(addLegend:!t,addTooltip:!t,isDonut:!f,shareYAxis:!t),title:Typesx2,type:pie))")),
                ko.observable(new Panel(5, 2, 3, 2, "Geographic Spread", "http://" + "es_admin" + ":" + "HelloWorld" + "@" + domain.slice(2) + ":5601/app/kibana#/visualize/edit/Geo?embed=true&_g=(refreshInterval:(display:Off,pause:!f,value:0),time:(from:now-5y,mode:quick,to:now))&_a=(filters:!(),linked:!f,query:(query_string:(analyze_wildcard:!t,query:\'*\')),uiState:(),vis:(aggs:!((id:\'1\',params:(),schema:metric,type:count),(id:\'2\',params:(autoPrecision:!t,field:location,precision:2),schema:segment,type:geohash_grid)),listeners:(),params:(addTooltip:!t,heatBlur:15,heatMaxZoom:16,heatMinOpacity:\'0.49\',heatNormalizeData:!t,heatRadius:25,isDesaturated:!t,mapType:Heatmap,wms:(enabled:!t,options:(attribution:\'\',format:image%2Fjpeg,layers:OSM-WMS,styles:\'\',transparent:!t,version:\'1.1.1\'),url:\'http:%2F%2Fows-tile.terrestris.de%2Fosm-basemap%2Fservice%3F\')),title:Geo,type:tile_map))")),
                ko.observable(new Panel(1, 1, 3, 2, "IP Ranges", "http://" + "es_admin" + ":" + "HelloWorld" + "@" + domain.slice(2) + ":5601/app/kibana#/visualize/create?embed=true&type=histogram&indexPattern=inbox&_g=(filters:!(),refreshInterval:(display:Off,pause:!f,value:0),time:(from:now-5y,mode:quick,to:now))&_a=(filters:!(),linked:!f,query:(query_string:(analyze_wildcard:!t,query:\'*\')),uiState:(vis:(colors:(Count:%2364B0C8))),vis:(aggs:!((id:\'1\',params:(),schema:metric,type:count),(id:\'2\',params:(field:ip,ipRangeType:fromTo,ranges:(fromTo:!((from:\'0.0.0.0\',to:'63.255.255.255'),(from:\'64.0.0.0\',to:\'127.255.255.255\'),(from:\'128.0.0.0\',to:\'191.255.255.255\'),(from:\'192.0.0.0\',to:\'255.255.255.255\')),mask:!((mask:\'0.0.0.0%2F1\'),(mask:\'128.0.0.0%2F2\')))),schema:segment,type:ip_range)),listeners:(),params:(addLegend:!t,addTimeMarker:!f,addTooltip:!t,defaultYExtents:!f,mode:stacked,scale:linear,setYExtents:!f,shareYAxis:!t,times:!(),yAxis:()),title:\'New%20Visualization\',type:histogram))")),
                ko.observable(new Panel(1, 1, 3, 2, "Timeline", "http://" + "es_admin" + ":" + "HelloWorld" + "@" + domain.slice(2) + ":5601/app/kibana#/visualize/edit/Timeline?embed=true&_g=(filters:!(),refreshInterval:(display:Off,pause:!f,value:0),time:(from:now-5y,mode:quick,to:now))")),
                ko.observable(new Panel(1, 1, 2, 2, "Word cloud", "http://" + "es_admin" + ":" + "HelloWorld" + "@" + domain.slice(2) + ":5601/app/kibana#/visualize/create?embed=true&type=tagcloud&indexPattern=inbox&_g=(filters:!(),refreshInterval:(display:Off,pause:!f,value:0),time:(from:now-5y,mode:quick,to:now))&_a=(filters:!(),linked:!f,query:(query_string:(analyze_wildcard:!t,query:\'*\')),uiState:(),vis:(aggs:!((id:\'1\',params:(),schema:metric,type:count),(id:\'2\',params:(field:data.summary.title,order:desc,orderBy:\'1\',size:25),schema:segment,type:terms)),listeners:(),params:(font:serif,fontStyle:normal,fontWeight:normal,fromDegree:0,maxFontSize:72,minFontSize:18,orientations:1,spiral:archimedean,textScale:linear,timeInterval:500,toDegree:0),title:\'New%20Visualization\',type:tagcloud))"))
            ]);
        },
        onShow: function () {
            $("#dashboard_main_grid").gridster({
                widget_margins: [6, 6],
                widget_base_dimensions: [250, 225],
                autogrow_cols: true,
                extra_cols: 1,
                resize: {
                    enabled: true,
                    max_size: [3, 3]
                }
            });
        }
    });
});
