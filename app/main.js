import m from '/scripts/modules/mithril.min.js';
import Log from '/scripts/views/log.js'

export function init() {
	let main = document.getElementById('main');
	m.route.prefix('#') // prevents page from reloading on route change
	m.route(main, '/log/', {
		'/log/': Log,
	});
}

window.addEventListener('DOMContentLoaded', init);