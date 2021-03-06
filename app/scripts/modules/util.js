import m from '../modules/mithril.js';

export let navBar = {
	view: function() {
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

export function actionColor(s) {
    if (s.includes("in")) {
        return "green";
    }
    else {
        return "red";
    }
}

export let inputBox = {
    view: function(vnode) {
        return [
                m('.hero-body', {style: 'align-items: start;'},
                    m('.container.has-text-centered',
                        m('div.column.is-4.is-offset-4',
                            m('.box',
                                m('h3.title', vnode.attrs.title),
                                m('.field',
                                    m('.control',
                                        m('input#student_id.input.is-large.is-fullwidth.has-text-centered',
                                        {type:'number', placeholder:'2019240', autofocus: 'true', onkeydown: (e) => vnode.attrs.kd(e)})
                                    )
                                ),
                                m('button.button.is-primary.is-block.is-info-.is-large.is-fullwidth', {type: 'button', onclick: vnode.attrs.clickFunc},'Submit'),
                            ),
                        )
                    )
                )
        ];
    }
}

function z(n) {
    return n > 9 ? n : '0'+n;
}

export function formatDate(d, time=true) {
    if (d == null) { return ""; }
    let s;
    if (time) {
        s = [z(d.getMonth()+1), '/', z(d.getDate()), '/', d.getFullYear(), ', ', d.toLocaleTimeString()].join('');
    } else {
        s = [z(d.getMonth()+1), '/', z(d.getDate()), '/', d.getFullYear()].join('');
    }
    return s;
}

export async function request(method, hash, data) {
    if (data === "") {
        let r = await m.request({
            method: method,
            url: window.location.origin + hash
        }).catch(function(e) {
            alert(e.message);
        });
        return r;
    } else {
        let r = await m.request({
            method: method,
            url: window.location.origin + hash,
            data: data
        }).catch(function(e) {
            alert(e.response);
        });
        return r;
    }
}

let Table = {
    view: function(vnode) {
        return m("table.table", vnode.attrs.tableAttrs,
                m("thead",
                  m("tr", vnode.attrs.headers)),
                m("tbody",
                  vnode.children),
                 vnode.attrs.footers && m("tfoot",
                                          m("tr", vnode.attrs.footers)))
    }
}

function multisort(filters) {
    return function(A,B) {
        for (let filter of filters) {
            if (filter !== "") {
                let a = A[filter] || ""
                let b = B[filter] || ""

                if (a > b) {
                    return -1;
                }
                if (a < b) {
                    return 1;
                }
            }
        }
        return 0;
    }
}

// SorTable
//
// Input Params:
//    body: list of rows. Certain magic fields are read in the rowMapper.
//        - .id: sets the id attr on the row (renderer optimization)
//        - .selected: if truthy, sets the `is-selected` class on the row.
//    rowMapper: function applied to body. Wrapped in a `tr` implicitly.
//    backupKeys: list of js props to sort by. Applied after rowMapper. To pre-sort, apply to body.
//    headers: list of table headers as objects.
//        - .label: what is shown to the user
//        - .key: js prop it corresponds to (used for sorting)
//        - .attrs: attrs object applied to the th
//        - .choices: array of js prop values to switch between. If non-null, used _instead of_ sorting.
//            - .label: what is shown on the header decorator when it is active
//            - .key: the prop value compared against. If `row.column == key`, it is shown.
//    footers: list of table footers as objects.
//        - (same as headers but only uses .label and .attrs)
//    tableAttrs: standard attr map applied to the <table> node
//    prependRows: rows added to the top of the table, ignoring any sorts/filters.
let SorTable = {
    sortKey: "",
    filters: new Map(),

    isActive(vnode, key) {
        let filters = vnode.state.filters
        return ((filters.has(key) && filters.get(key)[0] != null) || vnode.state.sortKey === key)
    },
    headerDecoration(vnode, key) {
        let filters = vnode.state.filters
        if (filters.has(key)) {
            if (filters.get(key)[0] != null) {
                let filter = filters.get(key)[0]
                return [" [", filter.shortlabel || filter.label, "]"]
            }
        }
    },

    oninit(vnode) {
        // Initialize the header toggle states for each header with a choices array
        vnode.attrs.headers.map(function(h) {
            if (h.choices) {
                let filterList = [null, ...h.choices]
                vnode.state.filters.set(h.key, filterList)
            }
        })
    },

    view(vnode) {
        return m(Table, {
            tableAttrs: vnode.attrs.tableAttrs,
            headers: vnode.attrs.headers.map(function(h) {
                if (h.key == null) {
                    return m("th", h.attrs, h.label)
                }
                return m("th.clickable", Object.assign({
                    class: [
                        h.choices? "choices" : "sort",
                        vnode.state.isActive(vnode, h.key)? "is-selected": "",
                    ].join(" "),
                    onclick: function() {
                        if (h.choices) {
                            let filter = vnode.state.filters.get(h.key)
                            let e = filter.shift()
                            filter.push(e)
                        } else {
                            if (vnode.state.sortKey === h.key) {
                                vnode.state.sortKey = "";
                            } else {
                                vnode.state.sortKey = h.key;
                            }
                        }
                    }
                }, h.attrs), [
                    h.label,
                    vnode.state.headerDecoration(vnode, h.key)
                ])
            }),
            footers: (vnode.attrs.footers)? vnode.attrs.footers.map(function(f) {
                return m("td", f.attrs, f.label)
            }) : null,
        }, [
            ...(vnode.attrs.prependRows? vnode.attrs.prependRows : []),
            ...vnode.attrs.body.filter(function(row) {
                if (row.selected) {
                    return true
                }
                for (let [col,filterList] of vnode.state.filters) {
                    if ((filterList[0] != null) &&
                        filterList[0].key !== row[col]) {
                        return false
                    }
                }
                return true
            }).sort(
                multisort([vnode.state.sortKey, ...vnode.attrs.backupKeys])
            )
        ].map(function(row) {
            return m("tr", {
                id: row.id,
                class: row.selected? "is-selected" : "",
            }, vnode.attrs.rowMapper(row))
        })
        )
    }
}


// EdiTable
//
// Extends from SorTable, adds buttons for editing each row, and (optionally) an add row ("+") button
// Input Params:
//    body, backupKeys, headers, tableAttrs, prependRows: same as in SorTable
//    rowMapper: same as in SorTable; only applies to rows that are not currently being edited
//    editingRowMapper: similar to rowMapper, but only applied to rows that *are* being edited
//    newRowFunc: onclick for the "+" button. If not defined, the button is not shown.
//            If this is falsey, the "+" button is not shown.
//    saveFunc: function called when the "Save" button is pressed, receives the list of modified rows.
let EdiTable = {
    view(vnode) {
        return m(SorTable, {
            tableAttrs: vnode.attrs.tableAttrs,
            headers: [
                ...vnode.attrs.headers,
                {
                    key: null,
                    attrs: {class: "button-column"},
                    label: (vnode.attrs.newRowFunc) &&
                        m("button.button.is-small.editable-add", {onclick: vnode.attrs.newRowFunc}, "+")
                },
            ],
            prependRows: vnode.attrs.prependRows,
            body: vnode.attrs.body,
            rowMapper(row) {
                if (row.static) {
                    return [
                        ...vnode.attrs.rowMapper(row),
                        m("td")
                    ]
                }

                if (row.editing) {
                    return [
                        ...vnode.attrs.editingRowMapper(row),
                        m("td", m("button.button.editable-edit", {
                            onclick() {
                                row.editing = false
                                return
                            }
                        }, "Done"))
                    ]
                } else {
                    return [
                        ...vnode.attrs.rowMapper(row),
                        m("td", m("button.button.editable-edit", {
                            onclick() {
                                row.editing = true
                                row.selected = true
                                return
                            }
                        }, "Edit"))
                    ]
                }
            },
            footers: [{
                attrs: {
                    colspan: vnode.attrs.headers.length+1,
                    class: "editable-save-cell",
                    style: vnode.attrs.body.some(row => !row.editing && row.selected)? "display: none;" : "",
                },
                label: m("button.button.is-primary", {
                    onclick() {
                        vnode.attrs.saveFunc(vnode.attrs.body.filter(row => !row.editing && row.selected))
                    }
                }, "Save Changes")
            }],
            backupKeys: vnode.attrs.backupKeys,
        })
    }
}

// CreaTable
//
// Extends from EdiTable, "+" button adds a new row, editable in the same way as the others.
// Input Params:
//    body, backupKeys, headers, tableAttrs, rowMapper, editingRowMapper: same as in EdiTable
//    newRow: prototype object filled into a new row when the "+" button is pressed.
//    saveNewFunc: function which receives a list of all the newly-added rows when the save button is pressed.
//    saveEditedFunc: function which receives a list of all the modified rows when the save button is pressed.
let CreaTable = {
    newRows: [],
    view(vnode) {
        return m(EdiTable, {
            tableAttrs: vnode.attrs.tableAttrs,
            headers: vnode.attrs.headers,
            prependRows: vnode.state.newRows,
            body: vnode.attrs.body,
            newRowFunc() {
                let newRow = {}
                Object.assign(newRow, vnode.attrs.newRow)
                newRow.editing = true
                newRow.selected = true
                vnode.state.newRows.push(newRow)
                return
            },
            editingRowMapper: vnode.attrs.editingRowMapper,
            rowMapper: vnode.attrs.rowMapper,
            backupKeys: vnode.attrs.backupKeys,
            saveFunc(editedRows) {
                vnode.attrs.saveNewFunc(vnode.state.newRows)
                vnode.attrs.saveEditedFunc(editedRows)
            }
        })
    }
}
