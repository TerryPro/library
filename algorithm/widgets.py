
import ipywidgets as widgets
from IPython.display import display, clear_output
from IPython import get_ipython
import json
import os
import pandas as pd
import pkgutil
import inspect
import importlib
import re
import algorithm

class AlgorithmWidget(widgets.VBox):
    def __init__(self, metadata_path=None, init_algo=None):
        super().__init__()
        
        self.metadata = self.load_metadata(metadata_path)
        self.categories = list(self.metadata.keys())
        self.init_algo_id = init_algo
        
        # Style
        self.layout.border = '1px solid #ddd'
        self.layout.padding = '10px'
        self.layout.margin = '5px 0'
        self.common_style = {'description_width': '100px'}
        self.common_layout = widgets.Layout(width='98%')
        
        # Widgets
        self.category_dropdown = widgets.Dropdown(
            options=self.categories,
            description='类别:',
            style=self.common_style,
            layout=self.common_layout
        )
        
        self.algorithm_dropdown = widgets.Dropdown(
            description='算法:',
            style=self.common_style,
            layout=self.common_layout
        )
        
        self.description_output = widgets.Output()
        self.params_container = widgets.VBox()
        self.code_output = widgets.Output()
        
        self.generate_btn = widgets.Button(
            description='查看代码',
            button_style='primary',
            icon='code'
        )
        self.run_btn = widgets.Button(
            description='执行',
            button_style='warning',
            icon='play'
        )
        
        # Event Listeners
        self.category_dropdown.observe(self.on_category_change, names='value')
        self.algorithm_dropdown.observe(self.on_algorithm_change, names='value')
        self.generate_btn.on_click(self.on_generate_click)
        self.run_btn.on_click(self.on_run_click)
        
        # Init Layout
        header_widgets = []
        if not self.init_algo_id:
             header_widgets.append(widgets.HBox([self.category_dropdown, self.algorithm_dropdown]))
             header_widgets.append(widgets.HTML('<hr>'))

        self.children = header_widgets + [
            self.description_output,
            # Widgets.HTML('<hr>'), # Remove redundant separator line if we want cleaner UI? Or keep it?
            # User wants: "仅显示下面的输入配置和输出配置"
            # If init_algo provided, we hide selectors.
            # Maybe keep description as it is useful context.
            self.params_container,
            widgets.HTML('<hr>'),
            widgets.HBox([self.generate_btn, self.run_btn]),
            self.code_output
        ]
        
        # Trigger Init
        if self.categories:
            # If init_algo is specified, try to find it
            found = False
            if self.init_algo_id:
                for cat, algos in self.metadata.items():
                    # Check if target algo is in this category
                    target_algo = next((a for a in algos if a['id'] == self.init_algo_id), None)
                    
                    if target_algo:
                        self.category_dropdown.value = cat
                        
                        # Manually trigger category change logic to populate algorithm dropdown options
                        # Self.category_dropdown.options should be set already by __init__ -> on_category_change({'new': categories[0]})?
                        # No, initially categories[0] is set. If target is in another category, we changed value above.
                        # But observe callback might be async or not immediate if we are in init? 
                        # Actually observe is sync usually. 
                        # But to be safe, let's call the handler directly or ensure options are set.
                        self.on_category_change({'new': cat})
                        
                        # Now options are [(name, algo_dict), ...]. 
                        # We must set value to the algo_dict, NOT the name string.
                        self.algorithm_dropdown.value = target_algo
                        found = True
                        break
            
            if not found:
                self.on_category_change({'new': self.categories[0]})
            
    def load_metadata(self, metadata_path):
        # Use introspection instead of loading JSON
        return self.scan_library()

    def scan_library(self):
        metadata = {}
        
        # Get category labels
        cat_labels = getattr(algorithm, 'CATEGORY_LABELS', {})
        
        path = algorithm.__path__
        prefix = algorithm.__name__ + "."
        
        for _, name, ispkg in pkgutil.walk_packages(path, prefix):
            if not ispkg:
                try:
                    mod = importlib.import_module(name)
                    for fname, func in inspect.getmembers(mod, inspect.isfunction):
                        # Only include functions defined in the module (not imported)
                        if func.__module__ == name:
                            doc = inspect.getdoc(func)
                            if doc and 'Algorithm:' in doc:
                                algo_info = self.parse_algo_doc(doc, func, fname)
                                if algo_info:
                                    cat_key = algo_info.get('category', 'Uncategorized')
                                    # Map category key to label if possible
                                    cat_label = cat_labels.get(cat_key, cat_key)
                                    
                                    if cat_label not in metadata:
                                        metadata[cat_label] = []
                                    metadata[cat_label].append(algo_info)
                except Exception as e:
                    # print(f"Error inspecting {name}: {e}")
                    pass
        return metadata

    def parse_algo_doc(self, doc, func, func_name):
        if not doc:
            return None
            
        # Parse Algorithm metadata
        algo_info = self.parse_algorithm_metadata(doc)
        if not algo_info:
            return None
            
        algo_info['id'] = func_name
        algo_info['template'] = inspect.getsource(func)
        
        # Parse Parameters
        params_dict = self.parse_docstring_params(doc)
        
        # Merge with signature
        sig = inspect.signature(func)
        args_list = []
        
        for name, param in sig.parameters.items():
            # Get type info
            param_type = "str"
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == int:
                    param_type = "int"
                elif param.annotation == float:
                    param_type = "float"
                elif param.annotation == bool:
                    param_type = "bool"
                elif param.annotation == list:
                    param_type = "list"
                elif hasattr(param.annotation, '__name__'):
                    param_type = param.annotation.__name__
            
            # Get default value
            default_val = param.default if param.default != inspect.Parameter.empty else None
            
            # Get docstring info
            p_info = params_dict.get(name, {})
            
            # Use type from docstring if available
            doc_type = p_info.get("type")
            if doc_type:
                 doc_type_lower = doc_type.lower()
                 if "list" in doc_type_lower:
                     param_type = "list"
                 elif "int" in doc_type_lower:
                     param_type = "int"
                 elif "float" in doc_type_lower:
                     param_type = "float"
                 elif "bool" in doc_type_lower:
                     param_type = "bool"
            
            if p_info.get("ignore"):
                continue
                
            # Determine role
            role = p_info.get("role")
            if not role:
                if name == 'df':
                    role = 'input'
                elif name == 'output_var':
                    role = 'output'
                else:
                    role = 'parameter'

            # Infer widget
            options = p_info.get("options")
            widget_type = p_info.get("widget", self.infer_widget_type(name, param_type, options))
            
            arg_def = {
                'name': name,
                'type': param_type,
                'default': default_val if default_val is not None else p_info.get('default'),
                'label': p_info.get("label", name.replace("_", " ").title()),
                'description': p_info.get("description", ""),
                'widget': widget_type,
                'options': options,
                'min': p_info.get("min"),
                'max': p_info.get("max"),
                'step': p_info.get("step"),
                'priority': p_info.get("priority", "critical"),
                'role': role
            }
            args_list.append(arg_def)

        algo_info['args'] = args_list
        
        # Parse Returns (if not already parsed by parse_algorithm_metadata or separate logic)
        # scan for Returns section if utility doesn't do it
        if 'returns' not in algo_info:
             algo_info['returns'] = self.parse_returns(doc)
             
        return algo_info

    def parse_algorithm_metadata(self, docstring):
        if not docstring:
            return {}
        
        metadata = {}
        lines = docstring.split('\n')
        in_algo_section = False
        
        for line in lines:
            stripped_line = line.strip()
            if not stripped_line:
                continue
                
            if stripped_line.startswith('Algorithm:'):
                in_algo_section = True
                continue
            
            if in_algo_section:
                if stripped_line.startswith('Parameters:') or stripped_line.startswith('Returns:') or stripped_line.startswith('Example:'):
                    break
                    
                match = re.match(r'^(\w+)\s*:\s*(.+)$', stripped_line)
                if match:
                    key = match.group(1)
                    value = match.group(2)
                    
                    if key == 'imports':
                        metadata[key] = [imp.strip() for imp in value.split(',') if imp.strip()]
                    else:
                        metadata[key] = value
        return metadata

    def parse_docstring_params(self, docstring):
        if not docstring:
            return {}
        
        params = {}
        lines = docstring.split('\n')
        in_params_section = False
        current_param = None
        param_indent = None
        
        for line in lines:
            stripped_line = line.strip()
            if not stripped_line:
                continue
                
            indent = len(line) - len(line.lstrip())
            
            if stripped_line.startswith('Parameters:'):
                in_params_section = True
                continue
            if stripped_line.startswith('Returns:') or stripped_line.startswith('Example:'):
                in_params_section = False
                break
                
            if in_params_section:
                # Matches: name (type): description
                # Improved regex to handle nested parens loosely if needed, but standard is (type)
                match = re.match(r'^(\w+)\s*(?:\((.+?)\))?\s*:\s*(.+)$', stripped_line)
                
                is_param_def = False
                if match:
                    if param_indent is None:
                        is_param_def = True
                    elif indent > param_indent:
                        is_param_def = False
                    else:
                        is_param_def = True
                
                if is_param_def:
                    if param_indent is None:
                        param_indent = indent
                    
                    current_param = match.group(1)
                    param_type_str = match.group(2)
                    desc = match.group(3)
                    params[current_param] = {"description": desc}
                    if param_type_str:
                        params[current_param]["type"] = param_type_str
                
                elif current_param:
                    meta_match = re.match(r'^(label|widget|priority|options|min|max|step|ignore|role|default)\s*:\s*(.+)$', stripped_line)
                    if meta_match:
                        key = meta_match.group(1)
                        value = meta_match.group(2)
                        
                        if key in ['min', 'max', 'step']:
                            try:
                                if '.' in value:
                                    value = float(value)
                                else:
                                    value = int(value)
                            except ValueError:
                                pass 
                        elif key == 'ignore':
                            value = value.strip().lower() == 'true'
                        elif key == 'options':
                            val_str = value.strip('[]')
                            if val_str:
                                # Safe split considering options might contain comma inside quotes? 
                                # For simplicity assume simple JSON-like list
                                # Try json load if it looks like list
                                if value.strip().startswith('[') and value.strip().endswith(']'):
                                     try:
                                         value = json.loads(value)
                                     except:
                                         value = [v.strip().strip("'").strip('"') for v in val_str.split(',')]
                                else:
                                     value = [v.strip().strip("'").strip('"') for v in val_str.split(',')]
                            else:
                                value = []
                        
                        params[current_param][key] = value
                    else:
                        # Continuation
                        params[current_param]["description"] += " " + stripped_line
        return params

    def parse_returns(self, docstring):
        if not docstring:
            return {}
        lines = docstring.split('\n')
        in_returns = False
        info = {}
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('Returns:'):
                in_returns = True
                continue
            
            if in_returns:
                if not stripped: continue
                # Basic parsing: type: desc
                if ':' in stripped:
                    parts = stripped.split(':', 1)
                    info['return'] = parts[0].strip()
                    info['description'] = parts[1].strip()
                else:
                    info['return'] = stripped
                break # Just get first line for now
        return info

    def infer_widget_type(self, name, param_type, options=None):
        if options:
            return "select" # or dropdown
        
        name_lower = name.lower()
        
        if "filepath" in name_lower or "file_path" in name_lower:
            return "file-selector" # Need to ensure we support this widget type
        if "columns" in name_lower or "column" in name_lower:
            if param_type == "list":
                return "column-selector" # Multi
            return "column-selector" # Single
        if "color" in name_lower:
            return "color-picker"
        
        if param_type == "bool":
            return "checkbox"
        if param_type == "int":
            return "input-number" # IntText
        if param_type == "float":
            return "input-number" # FloatText
            
        return "input-text"

    def on_category_change(self, change):
        cat = change['new']
        if cat in self.metadata:
            algos = self.metadata[cat]
            options = [(a['name'], a) for a in algos]
            self.algorithm_dropdown.options = options
            if options:
                self.algorithm_dropdown.value = options[0][1]

    def on_algorithm_change(self, change):
        algo = change['new']
        if not algo:
            return
            
        with self.description_output:
            clear_output()
            # If we are in "single algo mode" (init_algo_id), maybe we can hide description or make it more subtle?
            # User said "仅显示下面的输入配置和输出配置".
            # But description might be useful.
            # Let's keep it but make sure it renders cleanly.
            if not self.init_algo_id:
                  print(algo.get('description', ''))
            else:
                  # In compact mode, show description as HTML Label or simpler text?
                  # Or just hide it if user thinks it is noise.
                  # "不需要后面的字符串" was referring to the code snippet perhaps? No, likely referring to the dropdown widgets.
                  # Let's show description as HTML which is cleaner
                  display(widgets.HTML(f"<b>{algo.get('name')}</b>: {algo.get('description', '')}"))
            
        self.build_params_widgets(algo)
        self.code_output.clear_output()

    def get_dataframe_variables(self):
        """Get all DataFrame variable names in the user's namespace"""
        ip = get_ipython()
        if not ip:
            return []
        
        dfs = []
        user_ns = ip.user_ns
        for name, var in user_ns.items():
            if not name.startswith('_') and isinstance(var, pd.DataFrame):
                dfs.append(name)
        return sorted(dfs)

    def build_params_widgets(self, algo):
        widgets_list = []
        self.param_widgets_map = {}
        
        # 1. Input DataFrames (from inputs array or implicit args)
        inputs = algo.get('inputs', [])
        args = algo.get('args', [])
        
        # Combine inputs from 'inputs' field and 'args' with role='input'
        # To avoid duplicates if metadata has both
        processed_inputs = set()
        
        for inp in inputs:
            name = inp.get('name')
            if name and name not in processed_inputs:
                widgets_list.append(self.create_dataframe_selector(name, inp.get('label', name)))
                processed_inputs.add(name)
                
        for arg in args:
            name = arg.get('name')
            role = arg.get('role', '')
            
            if role == 'input' and name not in processed_inputs:
                 widgets_list.append(self.create_dataframe_selector(name, arg.get('label', name)))
                 processed_inputs.add(name)
                 continue
            
            if role == 'output':
                # Generally outputs are return values, but sometimes arguments specify output var name
                # We skip output config for now or add a simple text field if needed
                continue
                
            if role == 'parameter':
                w = self.create_parameter_widget(arg)
                if w:
                    widgets_list.append(w)
                    
        ret_config = algo.get('returns', {})
        ret_type = ret_config.get('return', '').strip()
        
        # Only show output config if there is a return type and it's not "None"
        if ret_type and ret_type.lower() != 'none':
            # Add output variable config
            # Default output name based on function name or valid identifier
            default_out = f"res_{algo['id']}"
            widgets_list.append(widgets.HTML("<b>输出配置:</b>"))
            
            w = widgets.Text(
                value=default_out,
                description='输出变量名:',
                placeholder='输入变量名以接收结果',
                style=self.common_style,
                layout=self.common_layout
            )
            self.param_widgets_map['__output_var__'] = w
            widgets_list.append(w)
            
        self.params_container.children = widgets_list

    def create_dataframe_selector(self, name, label):
        dfs = self.get_dataframe_variables()
        if not dfs:
            dfs = ['df'] # Default fallback
            
        w = widgets.Dropdown(
            options=dfs,
            description=f'{label} ({name}):',
            style=self.common_style,
            layout=self.common_layout
        )
        self.param_widgets_map[name] = w
        return w

    def create_parameter_widget(self, arg):
        name = arg.get('name')
        label = arg.get('label', name)
        w_type = arg.get('widget', '')
        p_type = arg.get('type', 'str')
        default = arg.get('default')
        options = arg.get('options')
        
        widget = None
        
        if options:
            widget = widgets.Dropdown(
                options=options,
                value=default if default in options else options[0],

                description=label,
                style=self.common_style,
                layout=self.common_layout
            )
        elif p_type == 'bool' or w_type == 'checkbox':
            widget = widgets.Checkbox(
                value=bool(default),
                description=label,
                style=self.common_style,
                layout=self.common_layout
            )
        elif p_type == 'int':
            widget = widgets.IntText(
                value=int(default) if default is not None else 0,
                description=label,
                style=self.common_style,
                layout=self.common_layout
            )
        elif p_type == 'float':
            widget = widgets.FloatText(
                value=float(default) if default is not None else 0.0,
                description=label,
                style=self.common_style,
                layout=self.common_layout
            )
        else: # str or default
            widget = widgets.Text(
                value=str(default) if default is not None else '',
                description=label,
                style=self.common_style,
                layout=self.common_layout
            )
            
        if widget:
            self.param_widgets_map[name] = widget
            
        return widget

    def generate_code(self):
        algo = self.algorithm_dropdown.value
        func_name = algo.get('id')
        
        # Collect args
        call_args = []
        
        # Process inputs first (convention)
        # Actually we need to match the function signature order if positional,
        # but Keywords args are safer.
        # existing metadata template implies keyword arguments are used in construction usually,
        # or we just use kwargs style.
        
        args_config = algo.get('args', [])
        # Inputs map
        
        for name, widget in self.param_widgets_map.items():
            if name == '__output_var__':
                continue
            
            val = widget.value
            
            # Find arg config to check type
            arg_def = next((a for a in args_config if a['name'] == name), None)
            # Or inputs def
            # For simplicity, if it's a dataframe selector, we pass variable name as is
            # If it's a string param, we quote it.
            
            is_df = False
            # Check if it was created as dataframe selector
            if isinstance(widget, widgets.Dropdown) and 'df' in name.lower() and arg_def is None: 
                 # Heuristic for inputs from 'inputs' array which don't have arg def
                 is_df = True
            elif arg_def and arg_def.get('role') == 'input':
                is_df = True
                
            if is_df:
                call_args.append(f"{name}={val}")
            else:
                # Value formatting directly from widget value
                if isinstance(val, bool):
                    v_str = "True" if val else "False"
                elif isinstance(val, (int, float)):
                    v_str = str(val)
                else:
                    # String
                    # Check if it looks like a list/dict literal
                    val_str = str(val).strip()
                    if (val_str.startswith('[') and val_str.endswith(']')) or \
                       (val_str.startswith('{') and val_str.endswith('}')) or \
                       (val_str.startswith('(') and val_str.endswith(')')):
                        v_str = val_str
                    # Check for "None"
                    elif val_str == "None":
                         v_str = "None"
                    else:
                        v_str = f"'{val_str}'"
                
                call_args.append(f"{name}={v_str}")
        
        # Imports
        imports = algo.get('imports', [])
        import_str = '\n'.join(imports) + '\n' if imports else ''
        
        # Function Call
        code = f"{import_str}# {algo.get('name')}\n"
        
        # We need the function definition if it's not imported from library
        # The instruction says "1，采用函数调用的方式生成代码；" (Generate code via function call)
        # But where is the function defined? 
        # The metadata has "template" which contains the full function definition.
        # But if the library is installed as a package (library.algorithm), we should import it?
        # Metadata "imports" array sometimes has "import globals" or "import pandas".
        # It doesn't seem to import the algorithm itself.
        # The `template` field is the function source code.
        # So we should probably output the template (function def) AND the call.
        
        template = algo.get('template', '')
        if template:
            code += template + "\n"
            
        
        # Output assignment
        output_var = None
        if '__output_var__' in self.param_widgets_map:
            val = self.param_widgets_map['__output_var__'].value.strip()
            if val:
                output_var = val
        
        call_expr = f"{func_name}({', '.join(call_args)})"
        
        if output_var:
            code += f"{output_var} = {call_expr}\n"
            # Auto-display the output if it's assigned
            code += f"{output_var}"
        else:
            code += call_expr
            
        return code

    def on_generate_click(self, b):
        code = self.generate_code()
        with self.code_output:
            clear_output()
            print(code)

    def on_run_click(self, b):
        code = self.generate_code()
        ip = get_ipython()
        if ip:
            with self.code_output:
                clear_output()
                # Show code being executed?
                # print(f"# Executing:\n{code}\n" + "-"*20)
                # Instead of run_cell which might redirect output else where,
                # we try exec for capturing output in this widget's context.
                # However, run_cell is better for magics. 
                # Let's try run_cell first, but usually output capture needs `capture_output` decorator or context.
                # widgets.Output context manager handles stdout/stderr.
                print("Running...")
                result = ip.run_cell(code)
                if result.error_in_exec:
                    print("Error during execution.")
                else:
                    print("Execution complete.")
