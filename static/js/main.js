// Generated by CoffeeScript 1.3.3
(function() {
  var handleScheduleUpdate, log, updateSize;

  log = function(msg) {
    console.log(msg);
    $.post("/log?msg=" + msg, {});
    $('#msgs').prepend("<p>" + msg + "</p>");
    $('#msgs').slideDown(333);
    return setTimeout((function() {
      return $('#msgs').slideUp(666);
    }), 2000);
  };

  updateSize = function() {
    log("Screen geometry is " + document.width + " x " + document.height);
    return log("Doc geometry is " + screen.width + " x " + screen.height);
  };

  handleScheduleUpdate = function(event, ui) {
    var schedule_key;
    console.log(ui.helper);
    log("Dropped " + (ui.helper.data('id')) + " at " + ui.position.left + "," + ui.position.top + " or (" + ui.offset.left + "," + ui.offset.left + ")");
    $(this).append($(ui.helper).clone());
    schedule_key = $('body').data('schedule');
    return $.post("/schedule/" + schedule_key, {
      "key": ui.helper.data('id'),
      "left": ui.position.left,
      "top": ui.position.top
    });
  };

  $(function() {
    var schedule_key;
    $('#msgs').hide();
    updateSize();
    $('.picture').draggable({
      stop: handleScheduleUpdate
    });
    $("#schedule").droppable();
    schedule_key = $('body').data('schedule');
    log("Schedule is " + schedule_key);
    if ((navigator.userAgent.indexOf('iPhone') !== -1) || (navigator.userAgent.indexOf('iPod') !== -1) || (navigator.userAgent.indexOf('iPad') !== -1)) {
      $("#picturebar").hide();
    }
    return $.getJSON("/schedule/" + schedule_key, function(data) {
      var domp, p, _i, _len, _ref;
      _ref = data.pictures;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        p = _ref[_i];
        domp = $(".picture").filter(function() {
          return $(this).data('id') === p.id;
        });
        log(domp);
        domp.css({
          top: p.top,
          left: p.left
        });
      }
      return log(data);
    });
  });

}).call(this);
