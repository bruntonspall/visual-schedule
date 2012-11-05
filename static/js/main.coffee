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
	console.log ui.helper
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
			stop: handleScheduleUpdate
	$("#schedule").droppable()
		
	schedule_key = $('body').data('schedule')
	log "Schedule is #{schedule_key}"
	if ((navigator.userAgent.indexOf('iPhone') != -1) || (navigator.userAgent.indexOf('iPod') != -1) || (navigator.userAgent.indexOf('iPad') != -1))
		$("#picturebar").hide()
	$.getJSON "/schedule/#{schedule_key}", (data) -> 
		for p in data.pictures
			domp = $(".picture").filter () -> $(this).data('id') == p.id
			log domp
			domp.css top: p.top, left: p.left
		log data
		
