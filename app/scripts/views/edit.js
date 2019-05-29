import m from '../modules/mithril.js';
import {navBar} from '../modules/util.js';

export function view() {
	return [
		m(navBar),
		m('p', 'hello')
	];
}

export default {view};
