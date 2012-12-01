log = (msg) ->
	console.log msg
	$.post "/log?msg=#{msg}", {}
	$('.msgs').prepend "<p>#{msg}</p>"
	$('.msgs').slideDown 333
	setTimeout (() -> 
		$('.msgs').slideUp 666
		), 2000

handleScheduleUpdate = (event, ui) ->
	log $(this)
	domp = $(".schedule .picture").filter () -> $(this).data('key') == ui.helper.data('key')
	domp.css top: ui.position.top, left: ui.position.left

	schedule_key = $('body').data('schedule')
	$.post "/schedule/#{schedule_key}", 
		"key": ui.helper.data('key'),
		"type": ui.helper.data('type'),
		"left": ui.position.left,
		"top": ui.position.top,
		(data) ->
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

	$('.picture').draggable
			# stop: handleScheduleUpdate,
			helper: "clone",
			opacity: 0.40
	$(".schedule").droppable
			accept: ".picture",
			drop: handleScheduleUpdate
	$(".picturebar").droppable
			accept: ".picture",
			drop: (event, ui) ->
				placementkey = ui.helper.data('key')
				original = $(".schedule .picture").filter () -> $(this).data('key') == ui.helper.data('key')
				$.ajax 
					type: 'DELETE',
					url: "/schedule/#{schedule_key}/#{placementkey}",
					success: (data) ->
						original.remove()


		
	schedule_key = $('body').data('schedule')
	log "Schedule is #{schedule_key}"
	$.getJSON "/schedule/#{schedule_key}", (data) -> 
		for p in data.pictures
			domp = $(".schedule .picture").filter () -> $(this).data('key') == p.id
			domp.css top: p.top, left: p.left
		
