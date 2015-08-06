"use strict";

$(function() {

    // Submit handler for main edit survey form
    // TODO: generalize for ajaxy submission of all forms (e.g. questions)
    $("#edit-survey")[0].onsubmit = function() {
        event.preventDefault();
        var id   = this.id;
        var url  = this.action;
        var data = $(this).serialize();
        var resp = $("#"+id+"-messages");
        var post = $.post(url, data);
        resp.stop(true,true).hide().fadeIn()
            .removeClass("error success").addClass("info")
            .html("⌚ Saving changes...");
        post.done(function(data) {
            if (data.success){
                resp.stop(true,true).show()
                    .removeClass("error info").addClass("success")
                    .html("✓ Changes saved")
                    .delay(2000).fadeOut(1000);
            } else {
                var error = '';
                for (var field in data){
                    error += (error.length ? ", " : "") + data[field].join(', ');
                }
                resp.stop(true,true).show()
                    .removeClass("success info").addClass("error")
                    .html("✗ Error: " + error);
            }
        });
        post.fail(function(){
            resp.show().removeClass("success info").addClass("error").html("✗ An unknown error occurred");
        });
        return false;
    };

    // Handler for Add Question button
    $("#edit-survey-add-question")[0].onclick = function() {
        var url = $("#edit-survey")[0].action + '/questions/add';
        console.log(url);
        var resp = $("#edit-survey-add-question-messages");
        resp.stop(true,true).hide().fadeIn()
            .removeClass("error success").addClass("info")
            .html("⌚ Adding question...");
        var get = $.get(url);
        get.done(function(data) {
            if (data.success){
                resp.stop(true,true).show()
                    .removeClass("error info").addClass("success")
                    .html("✓ Question added")
                    .delay(2000).fadeOut(1000);
                console.log(data.question);
                // TODO: dynamically render question form here
            } else {
                resp.stop(true,true).show()
                    .removeClass("success info").addClass("error")
                    .html("✗ Error: " + data.error);
            }
        });
        get.fail(function(){
            resp.show().removeClass("success info").addClass("error").html("✗ An unknown error occurred");
        });
    };

});
