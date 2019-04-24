import m from '../modules/mithril.min.js';

let inputBox = {
	view: function(vnode) {
		return [
	         m('.hero-body', {style: 'align-items: start;'},
	           m('.container.has-text-centered',
	             m('div.column.is-4.is-offset-4',
	               m('.box',
	                   m('h3.title', 'Student ID'),
	                   m('.field',
	                     m('.control',
	                       m('input#phoneNumber.input.is-large.is-fullwidth.has-text-centered',
	                         {type:'number', placeholder:'2019240', autofocus: true})
	                      )
	                    ),
	                   m('button.button.is-primary.is-block.is-info-.is-large.is-fullwidth', 'Submit'),
	                ),
	              )
	            )
	          )
		];
	}
}

let navBar = {
	view: function(vnode) {
		return [
			m('nav.navbar', {role: 'navigation'},
				m('.navbar-brand',
					m('a.navbar-burger.burger', {role: 'button', 'aria-expanded': false, 'data-target': 'navbar-eca', 'aria-label': 'menu'},
						m('span', {'aria-hidden': true}),
						m('span', {'aria-hidden': true}),
						m('span', {'aria-hidden': true}),
						m('span', {'aria-hidden': true}),
					),
				),
				m('.navbar-menu', {id: 'navbar-eca'},
					m('.navbar-start',
						m('a.navbar-item[href=/#/home/]', 'Check-In/Out'),
						m('a.navbar-item[href=/#/logs/]', 'View Logs'),
						m('a.navbar-item[href=/#/search/]', 'Search Student'),
						m('a.navbar-item[href=/#/edit/]', 'Edit Roster'),
					),
				),
			),
		];
	}
}

export function view() {
	return [
		m(navBar),
		m(inputBox)
	];
}

export default {view};