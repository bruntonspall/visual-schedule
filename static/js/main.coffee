log = (msg) ->
	console.log msg
	$.post "/log?msg=#{msg}", {}
	$('#msgs').prepend "<p>#{msg}</p>"
	$('#msgs').slideDown 333
	setTimeout (() -> 
		$('#msgs').slideUp 666
		), 2000

updateSize = () ->
	log "Screen geometry is #{document.width} x #{document.height}"
	log "Doc geometry is #{screen.width} x #{screen.height}"

handleScheduleUpdate = (event, ui) ->
	log "Dropped #{ui.helper.data('id')} at #{ui.position.left},#{ui.position.top} or (#{ui.offset.left},#{ui.offset.left})"
	$(this).append($(ui.helper).clone());
	schedule_key = $('body').data('schedule')
	$.post "/schedule/#{schedule_key}", 
		"key": ui.helper.data('id'),
		"left": ui.position.left,
		"top": ui.position.top

$ () -> 
	$('#msgs').hide()
	updateSize()

	$('.picture').draggable
			stop: handleScheduleUpdate,
			helper: "clone",
			opacity: 0.40
	$("#schedule").droppable()
		
	schedule_key = $('body').data('schedule')
	log "Schedule is #{schedule_key}"
	# $.getJSON "/schedule/#{schedule_key}", (data) -> 
	# 	for p in data.pictures
	# 		domp = $(".picture").filter () -> $(this).data('id') == p.id
	# 		domp.css top: p.top, left: p.left
		
