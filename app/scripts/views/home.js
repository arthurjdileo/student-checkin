import m from '../modules/mithril.js';
import {navBar} from '../modules/util.js';

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
	                         {type:'number', placeholder:'2019240', autofocus: 'true'})
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

export function view() {
	return [
		m(navBar),
		m(inputBox)
	];
}

export default {view};
