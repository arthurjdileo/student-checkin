import m from './modules/mithril.min.js';
import Home from './views/home.js';

export function init() {
	console.debug('init');
	m.route.prefix('#') // prevents page from reloading on route change
	m.route(document.body, '/home/', {
		'/home/': Home,
	});
}

window.addEventListener('DOMContentLoaded', init);