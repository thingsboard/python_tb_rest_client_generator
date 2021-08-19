from os import listdir
from os.path import isfile, join
import importlib

from file import File
from function import Function
from generated_python_api_file import GeneratedPythonApiFile


class Generator:
    def __init__(self, path_to_ce: str, path_to_pe: str):
        self._path_to_ce = path_to_ce
        self._path_to_pe = path_to_pe
        self._pe_models_files = []
        self._ce_models_files = []
        self._pe_api_files = []
        self._ce_api_files = []
        self._clear_init_files()
        self._init_models_files()
        self._rest_client_base = GeneratedPythonApiFile(name='RestClientBase', have_init_section=True)
        self._rest_client_pe = GeneratedPythonApiFile(name='RestClientPE', have_init_section=True)
        self._rest_client_ce = GeneratedPythonApiFile(name='RestClientCE', have_init_section=False)

    @staticmethod
    def _clear_init_files():
        init_files = ['tb_rest_client/api/api_ce/__init__.py', 'tb_rest_client/api/api_pe/__init__.py',
                      'tb_rest_client/models/models_ce/__init__.py', 'tb_rest_client/models/models_pe/__init__.py']

        for file in init_files:
            with open(file, 'w') as f:
                f.write('')

    @staticmethod
    def _add_files(path: str, version: str) -> [File]:
        return tuple([File(path=path, filename=f, version=version) for f in listdir(path) if isfile(join(path, f))])

    def _init_models_files(self):
        self._pe_models_files = self._add_files(self._path_to_pe + 'swagger_client/models/', 'pe')
        self._ce_models_files = self._add_files(self._path_to_ce + 'swagger_client/models/', 'ce')
        self._ce_api_files = self._add_files(self._path_to_ce + 'swagger_client/api/', 'ce')
        self._pe_api_files = self._add_files(self._path_to_pe + 'swagger_client/api/', 'pe')

    @staticmethod
    def _write_file(path, file: File, data: [str], version: str):
        if file.filename != '__init__.py':
            with open(f'{path}{version}/' + file.filename, 'w') as f:
                f.writelines(data)

    @staticmethod
    def _read_file(path: str) -> [str]:
        with open(path, 'r') as handle_file:
            data = handle_file.readlines()

        if 'api' in path:
            data[19] = 'from tb_rest_client.api_client import ApiClient\n'

        return data

    @staticmethod
    def _import_class(abs_name: str, class_name: str) -> type:
        if class_name != 'Init':
            module = importlib.import_module(abs_name)
            return getattr(module, class_name)

    @staticmethod
    def _generate_functions(controller_name: str, method_list: filter) -> [Function]:
        return [Function(function_name=f.__name__, controller=controller_name,
                         params=''.join(f.__doc__.split(':param ')[2:]).split(':return')[0].replace('\n', '').split(
                             '        ')[:-1]) for f in method_list]

    @staticmethod
    def _write_init_file(file: File, module_path: str, version: str):
        # TODO: read class name from file
        with open(f'{module_path}{version}/__init__.py', 'a') as f:
            filename = file.filename.split('.')[0]
            if 'lw_m2m' in filename:
                class_name = ''.join(word.title() for word in filename[0:5].split('_')) + filename[5:6] + ''.join(
                    word.title() for word in filename[6:].split('_'))
                file.class_name = class_name
                f.write('from .' + filename + ' import ' + class_name + '\n')
            elif 'lwm_2m' in filename:
                class_name = (filename[0:1].upper() + filename[1:3] + filename[4:6]) + ''.join(
                    word.title() for word in filename[6:].split('_'))
                file.class_name = class_name
                f.write('from .' + filename + ' import ' + class_name + '\n')
            elif filename == 'url' or filename == 'uri':
                class_name = filename.upper()
                file.class_name = class_name
                f.write('from .' + filename + ' import ' + class_name + '\n')
            elif 'url' in filename:
                class_name = filename[0:3].upper() + ''.join(word.title() for word in filename[3:].split('_'))
                file.class_name = class_name
                f.write('from .' + filename + ' import ' + class_name + '\n')
            elif filename == '__init__':
                pass
            else:
                class_name = ''.join(word.title() for word in filename.split('_'))
                file.class_name = class_name
                f.write('from .' + filename + ' import ' + class_name + '\n')

    def _generate_files(self, path: str, ce_files: [File], pe_files: [File], mode: str):
        files_set = pe_files + ce_files

        ce_files_set = tuple([x.filename for x in ce_files])
        pe_files_set = tuple([x.filename for x in pe_files])

        for file in files_set:
            if file.filename in ce_files_set and file.filename in pe_files_set:
                handle_pe = self._read_file(
                    pe_files[pe_files_set.index(file.filename)].full_file_path)
                handle_ce = self._read_file(
                    ce_files[ce_files_set.index(file.filename)].full_file_path)

                if handle_ce == handle_pe:
                    self._write_file(path, file, handle_pe, 'ce')

                    if mode == 'models':
                        self._write_init_file(file, 'tb_rest_client/models/models_', 'ce')

                    if mode == 'controllers':
                        self._write_init_file(file, 'tb_rest_client/api/api_', 'ce')

                        if file.class_name:
                            klass = self._import_class('tb_rest_client.api.api_ce.' + file.filename.split('.')[0],
                                                       file.class_name)
                            method_list = filter(lambda x: x is not None, list(
                                map(lambda x: getattr(klass, x) if callable(getattr(klass, x)) and x.startswith(
                                    '__') is False and '_with_http_info' not in x else None, dir(klass))))

                            function_list = self._generate_functions(file.filename.split('.')[0], method_list)
                            s = ''
                            for i in function_list:
                                s += i.str_function + '\n'
                            self._rest_client_base.methods_section = s
                            self._rest_client_base.init = klass

                else:
                    self._write_file(path, file, handle_ce, 'ce')
                    self._write_file(path, file, handle_pe, 'pe')

                    if mode == 'models':
                        self._write_init_file(file, 'tb_rest_client/models/models_', 'ce')
                        self._write_init_file(file, 'tb_rest_client/models/models_', 'pe')

                    if mode == 'controllers':
                        self._write_init_file(file, 'tb_rest_client/api/api_', 'ce')
                        self._write_init_file(file, 'tb_rest_client/api/api_', 'pe')

                        if file.class_name:
                            ce_file = ce_files[ce_files_set.index(file.filename)]
                            pe_file = pe_files[pe_files_set.index(file.filename)]

                            # TODO: remake writing init file strategy
                            self._write_init_file(ce_file, 'tb_rest_client/api/api_', 'ce')
                            self._write_init_file(pe_file, 'tb_rest_client/api/api_', 'pe')

                            pe_klass = self._import_class(
                                f'tb_rest_client.api.api_pe.' + pe_file.filename.split('.')[0], pe_file.class_name)
                            ce_klass = self._import_class(
                                f'tb_rest_client.api.api_ce.' + ce_file.filename.split('.')[0], ce_file.class_name)

                            pe_method_list = filter(lambda x: x is not None, list(
                                map(lambda x: getattr(pe_klass, x) if callable(getattr(pe_klass, x)) and x.startswith(
                                    '__') is False and '_with_http_info' not in x else None, dir(pe_klass))))
                            pe_function_list = self._generate_functions(pe_file.filename.split('.')[0], pe_method_list)
                            pe_function_names_dict = {func.name: func for func in pe_function_list}

                            ce_method_list = filter(lambda x: x is not None, list(
                                map(lambda x: getattr(ce_klass, x) if callable(getattr(ce_klass, x)) and x.startswith(
                                    '__') is False and '_with_http_info' not in x else None, dir(ce_klass))))
                            ce_function_list = self._generate_functions(ce_file.filename.split('.')[0], ce_method_list)
                            ce_function_names_dict = {func.name: func for func in ce_function_list}

                            full_functions = set(ce_function_names_dict.keys()) & set(pe_function_names_dict.keys())
                            with_the_same_params = [func[0] for func in list(
                                filter(lambda x: x[0].params == x[1].params,
                                       [(ce_function_names_dict[function_name], pe_function_names_dict[function_name])
                                        for function_name in full_functions]))]
                            not_the_same_function = filter(lambda x: x not in with_the_same_params, full_functions)

                            try:
                                for i in with_the_same_params:
                                    self._rest_client_base.methods_section = i.str_function + '\n'

                                for i in not_the_same_function:
                                    if ce_function_names_dict.get(i):
                                        self._rest_client_ce.methods_section = ce_function_names_dict[
                                                                                   i].str_function + '\n'
                                        self._rest_client_base.init = ce_klass
                                    if pe_function_names_dict.get(i):
                                        self._rest_client_pe.methods_section = pe_function_names_dict[
                                                                                   i].str_function + '\n'
                                        self._rest_client_pe.init = pe_klass
                            except Exception as e:
                                print(e)
            else:
                handle_data = self._read_file(file.full_file_path)
                self._write_file(path, file, handle_data, file.version)

                if mode == 'models':
                    self._write_init_file(file, 'tb_rest_client/models/models_', file.version)

                if mode == 'controllers':
                    self._write_init_file(file, 'tb_rest_client/api/api_', file.version)

                    klass = self._import_class(f'tb_rest_client.api.api_{file.version}.' + file.filename.split('.')[0],
                                               ''.join(word.title() for word in file.filename.split('_')).split('.')[0])
                    method_list = filter(lambda x: x is not None, list(
                        map(lambda x: getattr(klass, x) if callable(getattr(klass, x)) and x.startswith(
                            '__') is False and '_with_http_info' not in x else None, dir(klass))))

                    function_list = self._generate_functions(file.filename.split('.')[0], method_list)

                    s = ''
                    for i in function_list:
                        s += i.str_function + '\n'

                    if file.version == 'ce':
                        self._rest_client_ce.methods_section = s
                        self._rest_client_base.init = klass
                    else:
                        self._rest_client_pe.methods_section = s
                        self._rest_client_pe.init = klass

        with open('tb_rest_client/rest_client_base.py', 'w') as f:
            f.writelines(self._rest_client_base.generate_file())

        with open('tb_rest_client/rest_client_pe.py', 'w') as f:
            f.writelines(self._rest_client_pe.generate_file())

        with open('tb_rest_client/rest_client_ce.py', 'w') as f:
            f.writelines(self._rest_client_ce.generate_file())

    def generate(self):
        self._generate_files('tb_rest_client/models/models_', self._ce_models_files, self._pe_models_files, 'models')
        self._generate_files('tb_rest_client/api/api_', self._ce_api_files, self._pe_api_files, 'controllers')
