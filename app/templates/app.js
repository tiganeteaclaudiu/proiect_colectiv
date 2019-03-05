
username = '{{ username }}';

console.log('user!: '+username);


jQuery(document).ready(function(){

current_family = '';

menu_options = {
	'user-menu' : {
		'user-menu-main-panel' : [
				{
					'name' : 'View parking lots',
					'link' : 'view-parking',
					funct : function() {
						query();
						}
				},
				{
					'name' : 'Reserve parking spot',
					'link' : 'reserve_spot',
					funct : function() {
						query();
						}
				},
				{
					'name' : 'Update personal info',
					'link' : 'update-personal',
					funct : function() {
						query();
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

function add_back_button(menu_option) {
	element = $('<a class="sidebar-back-button"><div class="side-menu-option">Back</div></a>');
	$("#side-menu").append(element);
	$("#side-menu > .sidebar-back-button").click(function(e) {
		e.preventDefault();
		load_sidebar_options(menu_option);
		show_content(menu_option+'-main-panel');
	});
}



function add_cursor_button_event(id,url,extra_data) {

	if (typeof extra_data === 'undefined') { extra_data = ''; }

	console.log("add_cursor_button_event");

	$(".cursor-button").click(function(e) {

		username = '{{ username }}';
		console.log("USERNAME: " + username);

		data = {
			'id' : id,
			'user' : username
		}

		if (extra_data !== '') {

			console.log("ADD CURSOR FOUND EXTRA DATA:  ");
			console.log(JSON.stringify(extra_data));

			for (var key in extra_data) {
				data[key] = extra_data[key];
			}
			console.log('DATA AFTER EXTRA: '+JSON.stringify(data));

		}

		$.ajax({
			url: url,
			method: 'POST',
			data: JSON.stringify(data)
		});

	});

}


// ---------------------------- BUTTON EVENTS 
$("#content-back-button").click(function(e) {
	e.preventDefault();
	console.log(current_family);
	// query_reminders();
	add_lists();
});
