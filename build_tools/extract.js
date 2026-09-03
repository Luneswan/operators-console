const fs = require('fs');
const src = fs.readFileSync('C:/Users/anasa/Downloads/python-operators-console.html','utf8');
const start = src.indexOf('<script>');
const body = src.slice(start+8);
// find the segment containing the data decls up to the first non-data code
const names = ['PHASES','MATRIX','SHELF','FIELDS','CERTS','CHANNELS','QUIZZES'];
// Evaluate the whole prelude: take from 'const R =' to 'const KEY'
const a = body.indexOf('const R =');
const b = body.indexOf('const KEY');
const code = body.slice(a,b);
const fn = new Function(code + '\nreturn {' + names.join(',') + '};');
const out = fn();
for (const n of names) console.error(n, Array.isArray(out[n]) ? out[n].length : typeof out[n]);
fs.writeFileSync('raw_curriculum.json', JSON.stringify(out,null,1));
