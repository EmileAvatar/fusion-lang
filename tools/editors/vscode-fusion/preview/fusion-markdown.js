// Fusion code in VS Code's Markdown preview (Task 36.9): ```fusion blocks coloured with Fusion's colours.
// Written by tools/editors/build_grammar.py from src/lexer/keywords.py and colors.json - do not edit by hand.
'use strict';

const WORDS = {
  "keyword": [
    "End",
    "async",
    "await",
    "break",
    "case",
    "catch",
    "continue",
    "else",
    "end",
    "fall",
    "finally",
    "for",
    "foreach",
    "go",
    "if",
    "loop",
    "match",
    "return",
    "step",
    "throw",
    "try",
    "while"
  ],
  "declaration": [
    "Enum",
    "cast",
    "class",
    "constructor",
    "enum",
    "extends",
    "func",
    "function",
    "get",
    "implements",
    "import",
    "includes",
    "inherits",
    "interface",
    "namespace",
    "new",
    "property",
    "set",
    "struct",
    "template"
  ],
  "modifier": [
    "Shared",
    "Weak",
    "abstract",
    "byRef",
    "byVal",
    "const",
    "fixed",
    "internal",
    "let",
    "nocopy",
    "noshare",
    "override",
    "private",
    "protected",
    "public",
    "readonly",
    "sealed",
    "service",
    "static",
    "var",
    "virtual"
  ],
  "type": [
    "Cloneable",
    "Collection",
    "Default",
    "Dictionary",
    "Entry",
    "Error",
    "Iterator",
    "List",
    "Map",
    "Number",
    "Rounding",
    "bool",
    "byte",
    "bytes",
    "char",
    "decimal",
    "double",
    "float",
    "int",
    "int128",
    "int256",
    "long",
    "money",
    "short",
    "string",
    "void"
  ],
  "operator": [
    "and",
    "in",
    "is",
    "not",
    "or"
  ],
  "literal": [
    "false",
    "null",
    "true"
  ],
  "this": [
    "super",
    "this"
  ],
  "reserved": [
    "assert",
    "atomic",
    "base",
    "channel",
    "check",
    "choice",
    "comptime",
    "default",
    "defer",
    "delete",
    "elif",
    "export",
    "extern",
    "goto",
    "hotpath",
    "impl",
    "lock",
    "macro",
    "module",
    "move",
    "mut",
    "nameof",
    "operator",
    "out",
    "record",
    "ref",
    "select",
    "self",
    "sizeof",
    "switch",
    "synchronized",
    "trait",
    "transaction",
    "type",
    "typeof",
    "union",
    "unsafe",
    "using",
    "volatile",
    "where",
    "yield"
  ]
};
const KIND = {};
for (const kind of Object.keys(WORDS)) {
  for (const word of WORDS[kind]) {
    KIND[word] = kind;
  }
}

function escapeHtml(text) {
  return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function span(role, text) {
  return '<span class="fz-' + role + '">' + escapeHtml(text) + '</span>';
}

// A string's escapes and {interpolations} coloured inside it
function stringHtml(text) {
  let out = '';
  let i = 0;
  let plain = '';
  const flush = () => { if (plain) { out += span('string', plain); plain = ''; } };
  while (i < text.length) {
    const c = text[i];
    if (c === '\\' && i + 1 < text.length) {
      flush();
      const m = /^\\(u\{[0-9A-Fa-f]+\}|u[0-9A-Fa-f]{4}|.)/.exec(text.slice(i));
      out += span('escape', m[0]);
      i += m[0].length;
    } else if (c === '{') {
      const close = text.indexOf('}', i);
      if (close > i) {
        flush();
        out += span('interpolation', text.slice(i, close + 1));
        i = close + 1;
      } else {
        plain += c;
        i += 1;
      }
    } else {
      plain += c;
      i += 1;
    }
  }
  flush();
  return out;
}

const RULES = [
  [/^\/\*[\s\S]*?(\*\/|$)/, 'comment'],
  [/^\/\/[^\n]*/, 'comment'],
  [/^"(\\.|[^"\\\n])*"?/, 'string'],
  [/^'(\\(u\{[0-9A-Fa-f]+\}|u[0-9A-Fa-f]{4}|.)|[^'\\\n])'/, 'char'],
  [/^(0[xX][0-9A-Fa-f_]+|0[bB][01_]+|0[oO][0-7_]+|\d[\d_]*(\.\d[\d_]*([eE][+-]?\d[\d_]*)?|[eE][+-]?\d[\d_]*)(dec|[mfFdD])?(?![A-Za-z0-9_])|\d[\d_]*(dec|m)(?![A-Za-z0-9_])|\d[\d_]*[Ll]?)/, 'number'],
  [/^[A-Za-z_][A-Za-z0-9_]*/, 'word'],
  [/^(\.\.\.|\?\.|\?\?|===|!==|==|!=|<=|>=|->|=>|::|[-+*\/%=<>!&|^~?:])/, 'operator'],
];

function highlightFusion(code) {
  let out = '';
  let rest = code;
  let previous = '';
  while (rest.length > 0) {
    let matched = null;
    for (const [regex, kind] of RULES) {
      const m = regex.exec(rest);
      if (m) {
        matched = [m[0], kind];
        break;
      }
    }
    if (!matched) {
      out += escapeHtml(rest[0]);
      rest = rest.slice(1);
      continue;
    }
    const [text, kind] = matched;
    if (kind === 'string') {
      out += stringHtml(text);
    } else if (kind === 'char') {
      out += span('string', text);
    } else if (kind === 'word') {
      const after = rest.slice(text.length);
      if (KIND[text] && !previous.endsWith('.')) {
        out += span(KIND[text], text);
      } else if (/^\s*\(/.test(after) && /^[a-z_]/.test(text)) {
        out += span('function', text);
      } else if (/^[A-Z]/.test(text)) {
        out += span('type', text);
      } else {
        out += escapeHtml(text);
      }
    } else {
      out += span(kind, text);
    }
    previous = text;
    rest = rest.slice(text.length);
  }
  return out;
}

function extendMarkdownIt(md) {
  const original = md.options.highlight;
  md.options.highlight = (code, lang, attrs) => {
    if ((lang || '').trim().split(/\s+/)[0].toLowerCase() === 'fusion') {
      return '<pre class="fusion-code"><code>' + highlightFusion(code) + '</code></pre>';
    }
    return original ? original(code, lang, attrs) : '';
  };
  return md;
}

function activate() {
  return { extendMarkdownIt };
}

module.exports = { activate, extendMarkdownIt, highlightFusion };
