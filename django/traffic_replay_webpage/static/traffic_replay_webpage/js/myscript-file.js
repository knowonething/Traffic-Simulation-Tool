var Upload = function (files, url, usage, file_desc) {
    this.files = files
    this.url = url
    this.usage = usage
    this.file_desc = file_desc
};

var clear_upload_modal = function(){
    $("#uploadModal").modal('hide')
    $("#uploadModal div.modal-footer button").removeAttr("disabled")
    $("#files-usage-upload").text("")
    $("#files-desc").val("")
    $("#uploaded-files").html("")
    $("#upload-process").css("width", "0%");
    $("#upload-process").attr("aria-valuenow", 0);
}

Upload.prototype.doUpload = function () {
    if (this.files.length == 0){
        toastr.warning("没有发现被选择的文件", "未选择文件", toastr_opts)
        $("#uploadModal div.modal-footer button").removeAttr("disabled")
        return
    }
    var that = this;
    var formData = new FormData();

    // add assoc key values, this will be posts values
    for (let i=0; i<this.files.length; i++){
        formData.append("file", this.files[i], this.files[i].name);
    }
    let usage = this.usage
    formData.append("upload_file", true);
    formData.append("usage", this.usage);
    formData.append("file_desc", this.file_desc);

    $.ajax({
        type: "POST",
        url: this.url,
        "dataType": 'json',
        xhr: function () {
            var myXhr = $.ajaxSettings.xhr();
            if (myXhr.upload) {
                myXhr.upload.addEventListener('progress', that.progressHandling, false);
            }
            return myXhr;
        },
        success: function (data) {
            if (data.length != 0){
                error_str = "以下文件传输失败，请检查文件是否和现有文件重名:"
                for (let i=0; i<data.length; i++){
                    error_str = error_str + "<br>" + data[i]
                }
                toastr.error(error_str, "文件上传失败", toastr_opts)
            }else{
                toastr.success("服务器提示文件上传成功", "文件上传成功", toastr_opts)
            }
            redraw_multi_selector(usage)
            setTimeout(clear_upload_modal, 2000)
        },
        error: function (error) {
            toastr.error("服务器提示文件上传失败", "文件上传失败", toastr_opts)
            setTimeout(clear_upload_modal, 2000)
        },
        async: true,
        data: formData,
        cache: false,
        contentType: false,
        processData: false,
        timeout: 60000
    });
};

Upload.prototype.progressHandling = function (event) {
    var percent = 0;
    var position = event.loaded || event.position;
    var total = event.total;
    var progress_bar_id = "#upload-process";
    if (event.lengthComputable) {
        percent = Math.ceil(position / total * 100);
    }
    // update progressbars classes so it fits your code
    $(progress_bar_id).css("width", percent + "%");
    $(progress_bar_id).attr("aria-valuenow", percent);
};

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

var set_upload_modal = function (files, usage) {
    if (files.length == 0){
        toastr.warning("没有发现被选择的文件", "未选择文件", toastr_opts)
        return
    }
    desc_str = "<p>以下文件将要上传:</p>"
    for (let i = 0; i < files.length; i++) {
        desc_str = desc_str + "<p>" + files[i].name + "</p>"
    }
    $("#uploaded-files").html(desc_str)
    $("#files-usage-upload").text(usage)
    $("#uploadModal").modal('show', {backdrop: 'static'})
    scrollTo(0,0)
}

var upload_input_selector = {
    "generate": "#generate-add form div a input",
    "simulate": "#simulate-add form div a input",
    "monitor": "#monitor-add form div a input",
}

var file_desc_infos = {
    "generate": "用户未指定描述信息，该文件仅用于生成流量",
    "simulate": "用户未指定描述信息，该文件仅用于模拟用户行为流量",
    "monitor": "用户未指定描述信息，该文件仅用于监视流量动态",
}

var webpage_base_url = ""

var bind_listener_for_upload = function(base_url){
    webpage_base_url = base_url
    $("#generate-add form button").on("click", function(){
        files = $(this).prev()[0].querySelector("input").files
        set_upload_modal(files, "generate")
    })
    $("#simulate-add form button").on("click", function(){
        files = $(this).prev()[0].querySelector("input").files
        set_upload_modal(files, "simulate")
    })
    $("#monitor-add form button").on("click", function(){
        files = $(this).prev()[0].querySelector("input").files
        set_upload_modal(files, "monitor")
    })
    $("#uploadModal div.modal-footer button:nth-child(1)").on("click", function(){
        $("#uploadModal div.modal-footer button").attr("disabled", "")
        usage = $("#files-usage-upload").text()
        files = $(upload_input_selector[usage])[0].files
        url = webpage_base_url + "upload-file/"
        file_desc = $("#files-desc").val()
        if (file_desc.length == 0){
            file_desc = file_desc_infos[usage]
        }
        var upload = new Upload(files, url, usage, file_desc)
        upload.doUpload()
    })
}

var delete_select = {
    "generate": "#generate-select",
    "simulate": "#simulate-select",
    "monitor": "#monitor-select",
}

var multi_selector_callback = function (data, file_usage) {
    $(delete_select[file_usage]).html("")
    innerHTML = ""
    for (let i = 0; i < data.length; i++) {
        item = data[i]
        let new_option = "<option value='" + item.file_name + "'>" + item.file_name + "</option>"
        innerHTML = innerHTML + new_option
    }
    $(delete_select[file_usage]).html(innerHTML)
    $(delete_select[file_usage]).multiSelect("refresh")
    $(delete_select[file_usage]).multiSelect("deselect_all")
}

var redraw_multi_selector = function(file_usage){
    let request_data = { "file_usage": file_usage }
    $.ajax({
        "dataType": 'json',
        "type": "POST",
        "url": webpage_base_url + "get-configs/",
        "data": request_data,
        retryMax: 2,
        "success": function(data){
            multi_selector_callback(data, file_usage)
        }
    });
}

var set_delete_modal = function(files, file_usage){
    if (files==null || files.length == 0){
        toastr.warning("没有发现被选择的文件", "未选择文件", toastr_opts)
        return
    }
    desc_str = "<p>以下文件将要删除:</p>"
    for (let i = 0; i < files.length; i++) {
        desc_str = desc_str + "<p>" + files[i] + "</p>"
    }
    $("#delete-files").html(desc_str)
    $("#files-usage-delete").text(file_usage)
    $("#deleteModal").modal('show', {backdrop: 'static'})
    scrollTo(0,0)
}

var clear_delete_modal = function(){
    $("#deleteModal").modal('hide')
    $("#deleteModal div.modal-footer button").removeAttr("disabled")
    $("#files-usage-delete").text("")
    $("#delete-files").html("")
}

var bind_listener_for_delete = function () {
    $("#generate-delete form button").on("click", function () {
        files = $("#generate-delete button").prev().children("select").val()
        set_delete_modal(files, "generate")
    })
    $("#simulate-delete form button").on("click", function () {
        files = $("#simulate-delete button").prev().children("select").val()
        set_delete_modal(files, "simulate")
    })
    $("#monitor-delete form button").on("click", function () {
        files = $("#monitor-delete button").prev().children("select").val()
        set_delete_modal(files, "monitor")
    })
    $("#deleteModal div.modal-footer button:nth-child(1)").on("click", function () {
        $("#deleteModal div.modal-footer button").attr("disabled", "")
        usage = $("#files-usage-delete").text()
        files = $(delete_select[usage]).val()
        let request_data = {}
        for (let i = 0; i < files.length; i++) {
            request_data[files[i]] = usage
        }
        $.ajax({
            "dataType": 'json',
            "type": "POST",
            "url": webpage_base_url + "delete-file/",
            "data": request_data,
            retryMax: 2,
            success: function (data) {
                if (data.length != 0) {
                    error_str = "以下文件删除失败:"
                    for (let i = 0; i < data.length; i++) {
                        error_str = error_str + "<br>" + data[i]
                    }
                    toastr.error(error_str, "文件删除失败", toastr_opts)
                } else {
                    toastr.success("服务器提示文件删除成功", "文件删除成功", toastr_opts)
                }
                redraw_multi_selector(usage)
                setTimeout(clear_delete_modal, 2000)
            },
            error: function (error) {
                toastr.error("服务器提示文件删除失败", "文件删除失败", toastr_opts)
                setTimeout(clear_delete_modal, 2000)
            },
        });
    })
}