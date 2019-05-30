import m from './modules/mithril.js';
import Home from './views/home.js';
import Edit from './views/edit.js';
import Logs from './views/logs.js'

export function init() {
	console.debug('init');
	m.route.prefix('#') // prevents page from reloading on route change
	m.route(document.body, '/home/', {
		'/home/': Home,
		'/edit/': Edit,
		'/logs/': Logs
	});
}

window.addEventListener('DOMContentLoaded', init);
