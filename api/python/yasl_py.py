import ctypes
import json
import os
import platform

class YASL:
    """A Python wrapper for the Go YASL processor shared library."""

    def __init__(self):
        """Initializes the wrapper by loading the Go shared library."""
        lib_name = self._get_lib_name()
        if not os.path.exists(lib_name):
            raise FileNotFoundError(
                f"Shared library '{lib_name}' not found. "
                f"Please compile it first with: go build -buildmode=c-shared -o {lib_name} yasl_processor.go"
            )
        else:
            print(f"DEBUG: Loading shared library: {lib_name}")

        # Load the shared library
        self._lib = ctypes.CDLL(lib_name)

        # Define the argument and return types for the exported Go function
        self._process_func = self._lib.ProcessYASL
        self._process_func.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
        self._process_func.restype = ctypes.c_char_p

    def _get_lib_name(self) -> str:
        root = os.path.dirname(os.path.abspath(__file__))
        if platform.system() == "Windows":
            return os.path.join(root, "yasl.dll")
        if platform.system() == "Darwin":
            return os.path.join(root, "yasl.dylib")
        return os.path.join(root, "yasl.so")

    def process_yasl(self, yaml: str, yasl: str, context: dict, yaml_data: dict = None, yasl_data: dict = None) -> bool:
        """
        Calls the Go function to process YAML and YASL, with optional import maps.
        Args:
            yaml: Main YAML file path or content.
            yasl: Main YASL file path or content.
            context: Context dictionary.
            yaml_data: Optional map of YAML imports.
            yasl_data: Optional map of YASL imports.
        Returns:
            dict: Processed result.
        """
        yaml_c = ctypes.c_char_p(yaml.encode('utf-8'))
        yasl_c = ctypes.c_char_p(yasl.encode('utf-8'))
        context_json_c = ctypes.c_char_p(json.dumps(context).encode('utf-8'))
        yaml_data_json_c = ctypes.c_char_p(json.dumps(yaml_data or {}).encode('utf-8'))
        yasl_data_json_c = ctypes.c_char_p(json.dumps(yasl_data or {}).encode('utf-8'))
        result_ptr = self._process_func(yaml_c, yasl_c, context_json_c, yaml_data_json_c, yasl_data_json_c)
        result_json = result_ptr.decode('utf-8')
        response = json.loads(result_json)
        if response.get("error") not in (None, "null"):
            raise Exception(f"Go processor error: {response['error']}")
        return True
