
$(function() {
    $('[data-action="like"]').click(like);
    $('[data-action="dislike"]').click(dislike);
});


function like()
{
    var like = $(this);
    var type = like.data('type');
    var pk = like.data('id');
    var action = like.data('action');
    var dislike = like.next();
    $("#span1").addClass("bluelike");
            $("#span2").addClass("blacklike");
            $("#span1").removeClass("blacklike");
            $("#span2").removeClass("bluelike");
    $.ajax({
        url : "/home/" + type +"/" + pk + "/" + action + "/",
        type : 'POST',
        data : { 'obj' : pk },

        success : function (json) {

            like.find("[data-count='like']").text(json.like_count);
            dislike.find("[data-count='dislike']").text(json.dislike_count);
        }
    });

        return false;
}

function dislike()
{
    var dislike = $(this);
    var type = dislike.data('type');
    var pk = dislike.data('id');
    var action = dislike.data('action');
    var like = dislike.prev();
    $("#span1").addClass("blacklike");
            $("#span2").addClass("bluelike");
            $("#span1").removeClass("bluelike");
            $("#span2").removeClass("blacklike");

    $.ajax({
        url : "/home/" + type +"/" + pk + "/" + action + "/",
        type : 'POST',
        data : { 'obj' : pk },

        success : function (json) {

            dislike.find("[data-count='dislike']").text(json.dislike_count);
            like.find("[data-count='like']").text(json.like_count);
        }
    });

    return false;
}
