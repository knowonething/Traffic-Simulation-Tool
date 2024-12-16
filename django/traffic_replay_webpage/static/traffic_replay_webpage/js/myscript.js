var info_table_td4_status_info = {
    "created": '<button type="button" class="btn btn-default btn-sm btn-icon icon-left"><i class="entypo-pencil"></i>终止任务</button>',
    "running": '<button type="button" class="btn btn-default btn-sm btn-icon icon-left"><i class="entypo-pencil"></i>终止任务</button>',
    "stopped": '<button type="button" class="btn btn-danger btn-sm btn-icon icon-left"><i class="entypo-cancel"></i>删除任务</button>'
}
var info_table_build_td4 = function (status, creation_time, extra_info) {
    result = info_table_td4_status_info[status]
    result = result + '<button type="button" class="btn btn-info btn-sm btn-icon icon-left"><i class="entypo-info"></i>任务信息</button>'
    extra_info = JSON.parse(atob(extra_info))
    hidden_p = "<p hidden>" + extra_info["summary"]
    hidden_p = hidden_p + "<br>" + "任务创建时间: " + (new Date(parseFloat(creation_time) * 1000).toLocaleString("zh-CN"))
    if ("stopped time" in extra_info)
        hidden_p = hidden_p + "<br>" + "任务停止时间: " + (new Date(parseFloat(extra_info["stopped time"]) * 1000).toLocaleString("zh-CN"))
    hidden_p = hidden_p + "</p>"
    result = result + hidden_p
    if (webpage_task_type == "monitor"){
        if (status == "created"){
            return result
        }
        result = result + '<button type="button" class="btn btn-primary btn-sm btn-icon icon-left"><i class="entypo-brush"></i>捕获情况</button>'
    }
    return result
}
var info_table_td3_status_info = {
    "created": "<button type='button' class='btn btn-sm btn-info'>任务已下发</button>",
    "running": "<button type='button' class='btn btn-sm btn-success'>任务运行中</button>",
    "stopped": "<button type='button' class='btn btn-sm btn-danger'>任务已停止</button>"
}
var info_table_build_row = function (task_id, config_name, status, creation_time, extra_info) {
    td1 = task_id
    td2 = '<button type="button" class="btn btn-info btn-sm btn-icon icon-left"><i class="entypo-info"></i>配置文件内容</button>  ' + "<span>" + config_name + "</span>"
    td3 = info_table_td3_status_info[status]
    td4 = info_table_build_td4(status, creation_time, extra_info)
    return [td1, td2, td3, td4]
}

var show_info_modal = function(headinfo, bodyinfo){
    $("#infoModal h4.modal-title").html(headinfo)
    $("#infoModal div.modal-body div div").html(bodyinfo)
    $("#infoModal").modal('show', {backdrop: 'static'})
}

var info_table_bind_listener_for_buttons = function (row) {
    file_info_button = row.querySelectorAll("td:nth-child(2) button")[0]
    $(file_info_button).on("click", function () {
        file_name = $(this).next().text()
        let request_data = {
            "file_usage": webpage_task_type,
            "file_name": file_name
        }
        $.ajax({
        "type": "POST",
        "url": webpage_base_url + "get-content/",
        "data": request_data,
        retryMax: 2,
        "success": function(data){
            show_info_modal("配置文件内容: " + file_name, "<pre>" + data + "</pre>")
            scrollTo(0,0)
        }
        });
    })
    task_info_button = row.querySelectorAll("td:nth-child(4) button")[1]
    $(task_info_button).on("click", function (){
        p = $(this).next()
        show_info_modal("任务信息", p.prop("outerHTML"))
        $("#infoModal div.modal-body p").removeAttr("hidden")
        scrollTo(0,0)
    })
    stop_or_delete_button = row.querySelectorAll("td:nth-child(4) button")[0]
    $(stop_or_delete_button).on("click", function (){
        let request_data = {}
        let task_text = $(this).text()
        let related_row = $(this).parent().parent()[0]
        if (task_text == "终止任务"){
            show_info_modal("终止任务请求已发送", "终止任务请求已发送，请等待服务器响应。")
            scrollTo(0,0)
            request_data["action"] = "stop task"
            args = {
                "task_id": $(this).parent().parent()[0].childNodes[0].innerText
            }
            request_data["request_args"] = btoa(JSON.stringify(args))
            request_data["execution_time"] = (new Date()).getTime() / 1000.0
        }else if (task_text == "删除任务"){
            show_info_modal("删除任务请求已发送", "删除任务请求已发送，请等待服务器响应。")
            scrollTo(0,0)
            request_data["action"] = "delete task"
            args = {
                "task_id": $(this).parent().parent()[0].childNodes[0].innerText
            }
            request_data["request_args"] = btoa(JSON.stringify(args))
            request_data["execution_time"] = (new Date()).getTime() / 1000.0
        }else{
            return
        }

        $.ajax({
        "type": "POST",
        "dataType": 'json',
        "url": webpage_base_url + "request/",
        "data": request_data,
        retryMax: 2,
        "success": function(data){
            if (data["result"] == "success"){
                toastr.success("服务器提示" + task_text + "请求下发成功，如页面未更改，请稍后刷新页面。", "请求下发成功", toastr_opts)
                setTimeout(redraw_info_table, 2000, webpage_base_url + "get-tasks/", webpage_base_url, webpage_task_type)
            }else{
                toastr.error("服务器提示" + task_text + "请求下发失败。", "请求下发失败", toastr_opts)
            }
        },
        "error": function(){
            toastr.error("服务器提示" + task_text + "请求下发失败。", "请求下发失败", toastr_opts)
        }
        });
    })

    cap_info_button = row.querySelectorAll("td:nth-child(4) button:nth-child(4)")
    if (cap_info_button.length != 0){
        $(cap_info_button[0]).on("click", function(){
            task_id = $(this).parent().parent()[0].childNodes[0].innerText
            get_data_and_redraw_chart(task_id, -100)
        })
    }
}
var info_table_generate_callback = function (data) {
    $("#info-table").dataTable().fnClearTable()
    for (let i = 0; i < data.length; i++) {
        item = data[i]
        let new_row = info_table_build_row(item.task_id, item.task_config_file_name, item.task_status,
            item.task_creation_time, item.task_extra_info)
        $("#info-table").dataTable().fnAddData(new_row, false)
    }
    let all_rows = $("#info-table").dataTable().fnGetNodes()
    for (let i = 0; i < all_rows.length; i++) {
        info_table_bind_listener_for_buttons(all_rows[i])
    }
    $("#info-table").dataTable().fnDraw()
}

var webpage_base_url = ""
var webpage_task_type = ""

var redraw_info_table = function(url, base_url, task_type){
    webpage_base_url = base_url
    webpage_task_type = task_type
    let request_data = { "task_type": task_type }
    $.ajax({
        "dataType": 'json',
        "type": "POST",
        "url": url,
        "data": request_data,
        retryMax: 2,
        "success": info_table_generate_callback
    });
}

var toastr_opts = {
	"closeButton": true,
	"debug": false,
	"positionClass": "toast-top-full-width",
	"onclick": null,
	"showDuration": "300",
	"hideDuration": "1000",
	"timeOut": "5000",
	"extendedTimeOut": "1000",
	"showEasing": "swing",
	"hideEasing": "linear",
	"showMethod": "fadeIn",
	"hideMethod": "fadeOut"
};

var show_creation_modal = function(name){
    input = $("#creationModal form input#creation-file-name").val(name)
    $("#creationModal").modal('show', {backdrop: 'static'})
}

var config_table_bind_listener_for_buttons = function(row){
    file_info_button = row.querySelectorAll("td:nth-child(4) button")[1]
    $(file_info_button).on("click", function () {
        file_name = $(this).parent().parent()[0].childNodes[0].innerText
        let request_data = {
            "file_name": file_name,
            "file_usage": webpage_task_type,
        }
        $.ajax({
        "type": "POST",
        "url": webpage_base_url + "get-content/",
        "data": request_data,
        retryMax: 2,
        "success": function(data){
            show_info_modal("配置文件内容: " + file_name, "<pre>" + data + "</pre>")
            scrollTo(0,0)
        }
        });
    });
    create_task_button = row.querySelectorAll("td:nth-child(4) button")[0]
    $(create_task_button).on("click", function (){
        name = $(this).parent().parent()[0].childNodes[0].innerText
        show_creation_modal(name)
        scrollTo(0,0)
    });
}

var config_table_build_row = function (file_name, file_creation_time, file_description){
    td1 = file_name
    td2 = new Date(parseFloat(file_creation_time) * 1000).toLocaleString("zh-CN")
    td3 = file_description
    creation_button = '<button type="button" class="btn btn-default btn-sm btn-icon icon-left"><i class="entypo-right"></i>创建任务</button>'
    file_info_button = '<button type="button" class="btn btn-info btn-sm btn-icon icon-left"><i class="entypo-info"></i>配置文件内容</button>'
    td4 = creation_button + file_info_button
    return [td1, td2, td3, td4]
}


var config_table_generate_callback = function (data) {
    $("#config-table").dataTable().fnClearTable()
    for (let i = 0; i < data.length; i++) {
        item = data[i]
        let new_row = config_table_build_row(item.file_name, item.file_creation_time, item.file_description)
        $("#config-table").dataTable().fnAddData(new_row, false)
    }
    let all_rows = $("#config-table").dataTable().fnGetNodes()
    for (let i = 0; i < all_rows.length; i++) {
        config_table_bind_listener_for_buttons(all_rows[i])
    }
    $("#config-table").dataTable().fnDraw()
}

var redraw_config_table = function(url, base_url, task_type){
    webpage_base_url = base_url
    webpage_task_type = task_type
    let request_data = { "file_usage": task_type }
    $.ajax({
        "dataType": 'json',
        "type": "POST",
        "url": url,
        "data": request_data,
        retryMax: 2,
        "success": config_table_generate_callback
    });
}

var bind_creation_modal_submit = function(){
    $("#creationModal div.modal-footer button:nth-child(1)").on("click", function () {
        $("#creationModal").modal('hide')
        let args = {
            "task_config_file_name": $("#creation-file-name").val()
        }
        let stime = $("#creation-time").val()
        let tmp = stime.split(" ")
        let hms = tmp[0]
        let apm = tmp[1]
        tmp = hms.split(":")
        let hour = parseInt(tmp[0])
        let minute = parseInt(tmp[1])
        let second = parseInt(tmp[2])
        if (apm == "PM")
            hour = hour + 12
        stime = String(hour) + ":" + String(minute) + ":" + String(second)
        let sdate = $("#creation-date").val()
        let datetime = new Date(sdate + " " + stime).getTime() / 1000.0
        let request_data = {
            "action": webpage_task_type,
            "request_args": btoa(JSON.stringify(args)),
            "execution_time": datetime
        }
        $.ajax({
        "type": "POST",
        "url": webpage_base_url + "request/",
        "data": request_data,
        retryMax: 2,
        "success": function(data){
            if (data["result"] == "success"){
                toastr.success("服务器提示任务创建请求下发成功，如页面未更改，请稍后刷新页面。", "请求下发成功", toastr_opts)
                setTimeout(redraw_info_table, 2000, webpage_base_url + "get-tasks/", webpage_base_url, webpage_task_type)
            }else{
                toastr.error("服务器提示任务创建请求下发失败。", "请求下发失败", toastr_opts)
            }
        },
        "error": function(){
            toastr.error("服务器提示任务创建请求下发失败。", "请求下发失败", toastr_opts)
        }
        });
    })
}

var chart_id = "cap-info"
var chart_data = []
var xkey = "seconds"
var ykeys = []
var labels = []
var chart_object = null

var get_data_and_redraw_chart = function(task_id, time_after){
    let request_data = {
        "task_id": task_id,
        "time_after": time_after,
    }
    $.ajax({
        "type": "POST",
        "url": webpage_base_url + "get-records/",
        "data": request_data,
        retryMax: 2,
        "success": function(data){
            if (time_after < 0){
                if (data.length == 0){
                    scrollTo(0,0)
                    toastr.error("服务器提示未查询到相关捕获数据。", "未查询到数据", toastr_opts)
                    return
                }
                let monitor_info = JSON.parse(atob(data[0][1]))
                let protos = []
                for (let key in monitor_info["proto"]){
                    protos.push(key)
                }
                chart_data = []
                labels = protos
                ykeys = protos
                time_after = add_data(data)
                $("#"+chart_id).empty()
                chart_object = Morris.Line({
	                element: chart_id,
	                data: chart_data,
	                xkey: xkey,
	                ykeys: ykeys,
	                labels: labels,
	                redraw: true
                });
                $("#cap-info-chart-panel div.panel-title").text("流量捕获情况: " + task_id)
                if (time_after >= 0){
                    setTimeout(get_data_and_redraw_chart, 3000, task_id, time_after)
                }
                return
            }
            if (data.length == 0){
                setTimeout(get_data_and_redraw_chart, 3000, task_id, time_after)
                return
            }
            time_after = add_data(data)
            chart_object.setData(chart_data)
            if (time_after >= 0){
                setTimeout(get_data_and_redraw_chart, 3000, task_id, time_after)
            }
        },
    });
}

var add_data = function(data){
    let time_after = -1
    for(let i=0; i<data.length; i++){
        let item = data[i]
        let record_time = item[0]
        if (record_time < 0){
            return -1
        }
        let origin_data = JSON.parse(atob(item[1]))
        let plot_data = origin_data["proto"]
        plot_data["seconds"] = record_time * 1000
        chart_data.push(plot_data)
        time_after = record_time
    }
    return time_after
}