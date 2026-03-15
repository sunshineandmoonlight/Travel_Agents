const { parse } = require('@vue/compiler-sfc');
const fs = require('fs');

const content = fs.readFileSync('src/views/travel/steps/DetailedGuide.vue', 'utf8');

try {
  const { descriptor, errors } = parse(content);

  if (errors && errors.length > 0) {
    console.log('Parse errors:', errors.length);
    errors.forEach((err, i) => {
      console.log('Error ' + (i + 1) + ':', err.message);
      if (err.loc) {
        console.log('  Location:', JSON.stringify(err.loc));
      }
    });
  } else {
    console.log('SFC parsed successfully');

    // Check template specifically
    if (descriptor.template) {
      const templateContent = descriptor.template.content;
      console.log('Template length:', templateContent.length);

      // Count divs
      const openDivs = (templateContent.match(/<div[^/]*>/g) || []).length;
      const closeDivs = (templateContent.match(/<\/div>/g) || []).length;
      console.log('Open divs:', openDivs);
      console.log('Close divs:', closeDivs);
    }
  }
} catch (error) {
  console.log('ERROR:', error.message);
  console.log(error.stack?.split('\n').slice(0, 5).join('\n'));
}
