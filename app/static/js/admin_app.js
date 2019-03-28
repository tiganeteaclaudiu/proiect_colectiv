jQuery(document).ready(function(){
	
current_family = '';
parking_spot_id = '0';
parking_lot_name = '';

menu_options = {
	'user-menu' : {
		'user-menu-main-panel' : [
				{
					'name' : 'Manage Parking Lots',
					'link' : 'parking-lot-stats',
					funct : function() {
						query_parking_lot_stats();
						}
				}
			]
	}
}


//variable that holds the last page the user was on

load_sidebar_options('user-menu');



function load_menu_options() {
	console.log('load_menu_options called');
	for (var key in menu_options) {
		console.log('KEY: '+key);
		load_menu_options_events(key);
	}
}

function load_menu_options_events(key) {
	$("#"+key).click(function(e) {
		console.log('CLICKED: ');
		console.log($(this));
		load_sidebar_options(key);
	});
}

load_menu_options();

function show_content(id) {

	console.log('show_content id = '+id);

	load_sidebar_options(id);
	hide_all_content();
	$('#content_'+id).css('display','flex');
}

function hide_all_content() {
	$(".content-2col").css('display','none');
}

//Function adding sidebar options
//Supports adding sidebar options by either clicking items on the top menu or 
// items on the sidebar

//menu_options format:
//	-first level (dict) : top menu items
//	-second level (dict) : sidebar items that spawn another sidebar elements
//	-third layer (array of dicts) : sidebar elements
//		-name: name that appears on sidebar button
//		-link: link to content (content tabs have the format content_LINK)
//		-function: function to execute on clicking the sidebar element
function load_sidebar_options(menu_option,sidebar_option) {
	content = $("#"+menu_option);

	if (typeof sidebar_option === 'undefined') { sidebar_option = menu_option+"-main-panel"; }

	console.log('load_sidebar_options menu_option = '+menu_option);
	console.log('load_sidebar_options sidebar_option = '+sidebar_option);

	try {
		//first level: button is found on top bar
		if (menu_option in menu_options) {
			//sidebar is cleared, to be filled again
			$('#side-menu > a').remove();

			// menu = second level
			menu = menu_options[menu_option];
			console.log('load_sidebar_options menu: '+JSON.stringify(menu));
			console.log("load_sidebar_options sidebar option: "+JSON.stringify(menu[sidebar_option]));

			sidebar_options = menu[sidebar_option];
			//third level
			for (var i=0;i<=sidebar_options.length-1;i++) {

				console.log('load_sidebar_options sidebar[i]:' + JSON.stringify(sidebar_options[i]));
				
				option = sidebar_options[i];

				name = option['name'];
				link = option['link'];

				console.log('name = '+name);
				console.log('link = '+link);

				//sidebar element is created
				element = $('<a href="' + link +'"><div class="side-menu-option">'+ name +'</div></a>');

				//sidebar element is added
				$("#side-menu").append(element);

				//if there is a funct on the third level, it's bound to a click event
				if ('funct' in option) {
					funct = option['funct'];
					add_sidebar_funct(element,option['funct']);
				}

			}
			//load_menu_links method binds the click events to the new sidebar options
			//menu, menu_option are passed further for recursivity:
			//	if "link" is in menu, that means a newly created sidebar item is also on level 2
			//	 so it actually runs load_sidebar_options again for his own sidebar elements
			load_menu_links(menu, menu_option);

		}

	} catch(err) {
		console.log('No menu options for element  '+err);
	}
}

function add_sidebar_funct(element,funct) {

	element.click(function(e) {
		e.preventDefault();
		funct();
	});
}

//binds click events to new sidebar items
//	if "link" is in menu, that means a newly created sidebar item is also on level 2
//	 so it actually runs load_sidebar_options again for his own sidebar elements
function load_menu_links(menu, menu_option) {

	console.log('load_menu_links called: ');
	console.log('menu: '+JSON.stringify(menu))
	console.log('menu_option: '+JSON.stringify(menu_option))


	$("#side-menu > a").click(function(e) {
		e.preventDefault();
		link = $(this).attr('href');

		if (link in menu ) {
			console.log("FOUND AICI ASIDA SDASDASDASDASASD" + link);
			link2 = link;
			$('#content_'+link2).css('display','flex');
			load_sidebar_options(menu_option,link2);
			add_back_button(menu_option);
			show_content(link2);
			return '';
		}

		console.log("SHOWING LINK: =========> "+link);
		show_content(link);
	});

}

$("#view_parking-switch-button").click(function(e) {
	if ($("#view_parking-id-row").css("display") === 'none' ) {
		$("#view_parking-location-row").hide();
		$("#view_parking-id-row").css("display","flex");
		$("#view_parking-switch-button").html('Search by name');
	} else {
		$("#view_parking-id-row").hide();
		$("#view_parking-location-row").css("display","flex");
		$("#view_parking-switch-button").html('Search by ID');
	}
});

current_parking = '';

function load_parking(parking_file) {

	console.log('called now1');

	$("#parking-map-container").html('');

	$("#parking-map-container").load('/static/'+parking_file);
}

function load_sidepanel_parking_events() {

	$("#3321-brock-avenue").click(function(e) {
        e.preventDefault();
        console.log('now');
        //check if parking lot is not closed
        if(check_parking_lot_open('3321 Brock Avenue') == false) {
            load_parking('3321_brock_avenue.html');

            current_parking = '3321 Brock Avenue';
            parking_lot_name = current_parking;
    
            setTimeout(load_parking_spot_events,1000);
        } else {
            //parking is closed
            alert('Parking lot is closed for the day. Sorry for the inconvenience.');
        }

	});

	$("#9220-glover-road").click(function(e) {
        e.preventDefault();

        if(check_parking_lot_open('3321 Brock Avenue') == false) {
            load_parking('9920_glover_road.html');
            current_parking = '9220 Glover Road';
            parking_lot_name = current_parking;

            setTimeout(load_parking_spot_events,1000);
        } else {
            alert('Parking lot is closed for the day. Sorry for the inconvenience.');
        }
	});

}

function check_parking_lot_open(parking_lot_name) {
    data = JSON.stringify({
        'parking_lot_name' : parking_lot_name
    });

    $.ajax({
        url : '/check_parking_lot_open/',
        method : 'POST',
        data: data,
        success: function(data) {
            data = JSON.parse(data);
            return data['closed'];
        }
    });
        
}


function load_parking_spot_events() {

	console.log('unbinding');

	$(".parking-spot").unbind( "click" );

	console.log('LOAD SPOT EVENBT');

	$(".parking-spot").click(function(e) {
		e.preventDefault();
	
		id = $(this).attr('title');
		set_current_parking_spot_id(id);

		// load_calendar(true);
		$("#calendar-header").html('Select one day or drag across multiple days to set up a reservation!')
		show_content('reserve-spot');
		
	});
	
}

function set_current_parking_spot_id(id) {
	parking_spot_id = id;
	console.log('new parking_spot_id: '+parking_spot_id);

}

//--------------------- calendar


function query_reservations() {

	events = []

	$.ajax({
		url: '/query_reservations/',
		method: 'POST',
		data: JSON.stringify('{}'),
		success: function(data) {
		// 	console.log("query_events result:");
		// 	console.log(JSON.parse(data));
			data=JSON.parse(data);
			reservations = JSON.parse(data['reservations']);

			console.log('reservations ==============')
			console.log(reservations);

			load_calendar_reservations(reservations['reservations']);

			console.log('returning reservations');
			console.log(reservations['reservations']);

		return events['events'];
		}
	});
}

function load_calendar_reservations(reservations) {
	console.log('reservations ==============22')
	// console.log(reservations);

	// $("#calendar").fullCalendar('removeEvents');

	// setTimeout(function() {
	// 		$('#calendar').fullCalendar('addEventSource', reservations);
	// }, 500);

}

function delete_event(event) {

	data = {
		'id' : event.id
	};

	$.ajax({
		url : '/delete_event/',
		method : 'POST',
		data: JSON.stringify(data),
		success: function(data) {
			data = JSON.parse(data);
			$("#family-event-create-wrapper").hide();
			query_reservations();
		}
	});
}

$("#event-input-close-button").click(function(e) {
	e.preventDefault();
	// reload_list_input();
	$("#family-event-create-wrapper").hide();
});

function query_parking_lot_stats() {

    $.ajax({
		url : '/query_parking_lot_stats/',
		method : 'POST',
		data: JSON.stringify({}),
		success: function(data) {
			data = JSON.parse(data);
			// $("#family-event-create-wrapper").hide();
            // query_reservations();
            reservations = data['reservations'];
            profits = data['last_month_profits'];
            statuses = data['parking_lot_statuses'];

            $("#parking-lot-reservations-table tr").remove();
            
            html = `<tr>
                        <th> Parking lot name </th>
                        <th> User ID </th>
                        <th> Parking lot ID </th>
                    </tr>`;

            $("#parking-lot-reservations-table").append(html);

            $("#parking-lot-stats-table tr").remove();
            
            html = `<tr>
                        <th> Parking lot name </th>
                        <th> Currenly Occupied Spots</th>
                        <th> Last month's profit</th>
                    </tr>`;

            $("#parking-lot-stats-table").append(html);

            //add reservations to reservations table
            for (var key in reservations) {
                parking_lot_name = key;
                html = `
						<tr>
                            <td> `+parking_lot_name+` </td>
                            <td> `+(reservations[key].length)+` </td>
                            <td> `+profits[key]+` </td>
                    `;

                    if(statuses[key] === false) {
                        html += '<td style="background-color:red;color:white">CLOSE</td>';
                        html += '</tr>';
                        element = $(html);
                        $("#parking-lot-stats-table").append(element);

                        create_parking_lot_close_event(key,element);
                    } else {
                        html += '<td style="background-color:red;color:white">OPEN</td>';
                        html += '</tr>'
                        element = $(html);
                        $("#parking-lot-stats-table").append(element);

                        create_parking_lot_open_event(key,element);
                    }

                
            }
            
            //add reservations to reservations table
            for (var key in reservations) {

                for(var i=0;i<reservations[key].length;i++) {

                    user_id = reservations[key][i]['user_id'];
                    parking_spot_id = reservations[key][i]['parking_spot_id'];
                    parking_lot_name = key;

                    html = `
						<tr>
                        <td> `+parking_lot_name+` </td>
		                    <td> `+user_id+` </td>
		                    <td> `+parking_spot_id+` </td>
		                </tr>
                    `;
                    
                    $("#parking-lot-reservations-table").append(html);

                }

            
            }

            
		}
	});

}

function create_parking_lot_close_event(parking_lot_name,element) {

    data = JSON.stringify({
        'parking_lot_name' : parking_lot_name
    });

    element.off('click');

    element.click(function() {
        var r = confirm("Are you sure you want to close this parking lot?");
        if(r == true) {
            $.ajax({
                url : '/close_parking_lot/',
                method : 'POST',
                data: data,
                success: function(data) {
                    data = JSON.parse(data);
                    query_parking_lot_stats();
                }
            });
        }
    });


}

function create_parking_lot_open_event(parking_lot_name,element) {

    data = JSON.stringify({
        'parking_lot_name' : parking_lot_name
    });
 
    element.off('click');

    element.click(function() {
        var r = confirm("Are you sure you want to open this parking lot?");
        if(r == true) {
            $.ajax({
                url : '/open_parking_lot/',
                method : 'POST',
                data: data,
                success: function(data) {
                    data = JSON.parse(data);
                    query_parking_lot_stats();
                }
            });
        }
    });
 }





});