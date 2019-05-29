import m from '../modules/mithril.js';

export let navBar = {
	view: function(vnode) {
		return [
			m('nav.navbar', {role: 'navigation', 'aria-label': 'main navi'},
				m('.navbar-brand',
					m('a.navbar-item[href=/#/home/]',
						m('img', {src: './logo-shield.png'}),
					),
					m('a.navbar-burger.burger', {role: 'button', 'aria-expanded': 'false', 'data-target': '#mainNav', 'aria-label': 'menu'},
						m('span', {'aria-hidden': 'true'}),
						m('span', {'aria-hidden': 'true'}),
						m('span', {'aria-hidden': 'true'}),
					),
				),
				m('.navbar-menu#mainNav',
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
