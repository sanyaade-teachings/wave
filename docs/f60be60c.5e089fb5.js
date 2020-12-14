(window.webpackJsonp=window.webpackJsonp||[]).push([[232],{285:function(e,n,t){"use strict";t.r(n),t.d(n,"frontMatter",(function(){return c})),t.d(n,"metadata",(function(){return i})),t.d(n,"rightToc",(function(){return l})),t.d(n,"default",(function(){return p}));var a=t(2),o=t(6),r=(t(0),t(298)),c={title:"Toolbar"},i={unversionedId:"examples/toolbar",id:"examples/toolbar",isDocsHomePage:!1,title:"Toolbar",description:"Use toolbars to provide commands that operate on the content of a page.",source:"@site/docs/examples/toolbar.md",slug:"/examples/toolbar",permalink:"/wave/docs/examples/toolbar",editUrl:"https://github.com/h2oai/wave/edit/master/website/docs/examples/toolbar.md",version:"current",sidebar:"someSidebar",previous:{title:"Nav",permalink:"/wave/docs/examples/nav"},next:{title:"Tab",permalink:"/wave/docs/examples/tab"}},l=[],m={rightToc:l};function p(e){var n=e.components,c=Object(o.a)(e,["components"]);return Object(r.b)("wrapper",Object(a.a)({},m,c,{components:n,mdxType:"MDXLayout"}),Object(r.b)("p",null,"Use toolbars to provide commands that operate on the content of a page."),Object(r.b)("div",{className:"cover",style:{backgroundImage:"url("+t(453).default+")"}}),Object(r.b)("pre",null,Object(r.b)("code",Object(a.a)({parentName:"pre"},{className:"language-py"}),"from h2o_wave import main, app, Q, ui\n\n\n@app('/demo')\nasync def serve(q: Q):\n    q.page['nav'] = ui.toolbar_card(\n        box='1 1 4 1',\n        items=[\n            ui.command(\n                name='new', label='New', icon='Add', items=[\n                    ui.command(name='email', label='Email Message', icon='Mail'),\n                    ui.command(name='calendar', label='Calendar Event', icon='Calendar'),\n                ]\n            ),\n            ui.command(name='upload', label='Upload', icon='Upload'),\n            ui.command(name='share', label='Share', icon='Share'),\n            ui.command(name='download', label='Download', icon='Download'),\n        ],\n        secondary_items=[\n            ui.command(name='tile', caption='Grid View', icon='Tiles'),\n            ui.command(name='info', caption='Info', icon='Info'),\n        ],\n        overflow_items=[\n            ui.command(name='move', label='Move to...', icon='MoveToFolder'),\n            ui.command(name='copy', label='Copy to...', icon='Copy'),\n            ui.command(name='rename', label='Rename', icon='Edit'),\n        ],\n    )\n    await q.page.save()\n")))}p.isMDXComponent=!0},298:function(e,n,t){"use strict";t.d(n,"a",(function(){return s})),t.d(n,"b",(function(){return b}));var a=t(0),o=t.n(a);function r(e,n,t){return n in e?Object.defineProperty(e,n,{value:t,enumerable:!0,configurable:!0,writable:!0}):e[n]=t,e}function c(e,n){var t=Object.keys(e);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(e);n&&(a=a.filter((function(n){return Object.getOwnPropertyDescriptor(e,n).enumerable}))),t.push.apply(t,a)}return t}function i(e){for(var n=1;n<arguments.length;n++){var t=null!=arguments[n]?arguments[n]:{};n%2?c(Object(t),!0).forEach((function(n){r(e,n,t[n])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(t)):c(Object(t)).forEach((function(n){Object.defineProperty(e,n,Object.getOwnPropertyDescriptor(t,n))}))}return e}function l(e,n){if(null==e)return{};var t,a,o=function(e,n){if(null==e)return{};var t,a,o={},r=Object.keys(e);for(a=0;a<r.length;a++)t=r[a],n.indexOf(t)>=0||(o[t]=e[t]);return o}(e,n);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);for(a=0;a<r.length;a++)t=r[a],n.indexOf(t)>=0||Object.prototype.propertyIsEnumerable.call(e,t)&&(o[t]=e[t])}return o}var m=o.a.createContext({}),p=function(e){var n=o.a.useContext(m),t=n;return e&&(t="function"==typeof e?e(n):i(i({},n),e)),t},s=function(e){var n=p(e.components);return o.a.createElement(m.Provider,{value:n},e.children)},u={inlineCode:"code",wrapper:function(e){var n=e.children;return o.a.createElement(o.a.Fragment,{},n)}},d=o.a.forwardRef((function(e,n){var t=e.components,a=e.mdxType,r=e.originalType,c=e.parentName,m=l(e,["components","mdxType","originalType","parentName"]),s=p(t),d=a,b=s["".concat(c,".").concat(d)]||s[d]||u[d]||r;return t?o.a.createElement(b,i(i({ref:n},m),{},{components:t})):o.a.createElement(b,i({ref:n},m))}));function b(e,n){var t=arguments,a=n&&n.mdxType;if("string"==typeof e||a){var r=t.length,c=new Array(r);c[0]=d;var i={};for(var l in n)hasOwnProperty.call(n,l)&&(i[l]=n[l]);i.originalType=e,i.mdxType="string"==typeof e?e:a,c[1]=i;for(var m=2;m<r;m++)c[m]=t[m];return o.a.createElement.apply(null,c)}return o.a.createElement.apply(null,t)}d.displayName="MDXCreateElement"},453:function(e,n,t){"use strict";t.r(n),n.default=t.p+"assets/images/toolbar-6cae7b599ebdc78e77db0f536dc3392e.png"}}]);