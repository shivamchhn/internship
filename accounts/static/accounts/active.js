     $(document).ready(function() {
    $("nav div div ul li a").click(function(e)
    {
    $("nav div div ul li a").removeClass('active');
    $(this).addClass('active');
    });
    });