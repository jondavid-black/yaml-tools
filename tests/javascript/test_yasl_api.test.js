import { processYasl } from '../../api/javascript/yasl.js';

describe('YASL JavaScript API', () => {
  test('processYasl basic usage', () => {
    const yaml = 'foo: bar';
    const yasl = 'type: object';
    const context = { quiet: false };
    const yamlData = {};
    const yaslData = {};
    const result = processYasl(yaml, yasl, context, yamlData, yaslData);
    expect(typeof result).toBe('object');
    // Optionally check for expected keys/structure
  });

  test('processYasl error handling', () => {
    const yaml = '';
    const yasl = 'type: object';
    const context = { quiet: false };
    const yamlData = {};
    const yaslData = {};
    expect(() => processYasl(yaml, yasl, context, yamlData, yaslData)).toThrow('YAML input cannot be empty');
  });
});
