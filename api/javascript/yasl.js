const ffi = require('ffi-napi');
const path = require('path');
const os = require('os');

/**
 * Determines the correct shared library file name based on the OS.
 * @returns {string} The path to the shared library.
 */
function getLibraryPath() {
  const root = __dirname; // Assumes library is in the same directory
  switch (os.platform()) {
    case 'win32':
      return path.join(root, 'yasl.dll');
    case 'darwin':
      return path.join(root, 'yasl.dylib');
    default: // Linux and other Unix-like
      return path.join(root, 'yasl.so');
  }
}

// 1. Define the path to the compiled Go library.
const libraryPath = getLibraryPath();

// 2. Load the shared library and define the function signature.
// The first element of the array is the return type ('string' for *C.char).
// The second is an array of argument types (three *C.char).
const yaslProcessor = ffi.Library(libraryPath, {
  ProcessYASL: ['string', ['string', 'string', 'string']],
});

/**
 * Calls the Go function to process YAML and YASL content.
 * @param {string} yaml - A string containing the YAML content.
 * @param {string} yasl - A string containing the YASL schema content.
 * @param {object} context - An object for context (e.g., from CLI).
 * @returns {object} A dictionary representing the processed data model.
 * @throws {Error} If the Go function returns an error.
 */
export function processYasl(yaml, yasl, context) {
  // Convert the context object to a JSON string.
  const contextJson = JSON.stringify(context);

  // 3. Call the Go function via the FFI interface.
  const resultJson = yaslProcessor.ProcessYASL(yaml, yasl, contextJson);

  // 4. Parse the JSON response from Go.
  const response = JSON.parse(resultJson);

  // 5. Check for errors and throw if found.
  if (response.error) {
    throw new Error(`Go processor error: ${response.error}`);
  }

  return response.data;
}
