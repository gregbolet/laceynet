var fs = require('fs');

let fileName = new Date().toTimeString();
fs.writeFile('${fileName}.json', result.data, 'utf8', callback);

