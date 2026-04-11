const fs = require('fs');
// Mock marked
const marked = require('marked');

let val = `3. Montrer que pour tout $x \\in [1, +\\infty[$ :
$$0 < g(x) \\le \\frac{3}{2x}$$`;

let processedVal = val.replace(/\[([^\[\]]*?[=<>+\\-*\\^][^\[\]]*?)\]/g, '$$$$$1$$$$');
processedVal = processedVal.replace(/\(\((.*?)\)\)/g, '\\\\($1\\\\)');
processedVal = processedVal.replace(/\(([A-Za-z])\)/g, '\\\\($1\\\\)');
processedVal = processedVal.replace(/\(([A-Za-z]\\([A-Za-z]\\)[^()]*?)\)/g, '\\\\($1\\\\)');

console.log("PROCESSED:");
console.log(processedVal);

console.log("\nMARKED:");
console.log(marked.parse(processedVal));
