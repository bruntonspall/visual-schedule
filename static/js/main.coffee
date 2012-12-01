log = (msg) ->
	console.log msg
	$.post "/log?msg=#{msg}", {}
	$('.msgs').prepend "<p>#{msg}</p>"
	$('.msgs').slideDown 333
	setTimeout (() -> 
		$('.msgs').slideUp 666
		), 2000

updateSize = () ->
	log "Screen geometry is #{document.width} x #{document.height}"
	log "Doc geometry is #{screen.width} x #{screen.height}"

handleScheduleUpdate = (event, ui) ->
	domp = $(".schedule .picture").filter () -> $(this).data('key') == ui.helper.data('key')
	domp.css top: ui.position.top, left: ui.position.left

	schedule_key = $('body').data('schedule')
	$.post "/schedule/#{schedule_key}", 
		"key": ui.helper.data('key'),
		"type": ui.helper.data('type'),
		"left": ui.position.left,
		"top": ui.position.top,
		(data) ->
			log data
			if $(ui.helper).data('type') == 'picture'
				newpic = $(ui.helper).clone()
				newpic.attr('data-type', 'placement')
				newpic.attr('data-key', data)
				newpic.draggable
					stop: handleScheduleUpdate,
					helper: "clone",
					opacity: 0.40
				$('.schedule').append(newpic);


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
	$.getJSON "/schedule/#{schedule_key}", (data) -> 
		log data
		for p in data.pictures
			log p
			domp = $(".schedule .picture").filter () -> $(this).data('key') == p.id
			domp.css border: "2px red solid", top: p.top, left: p.left
		
