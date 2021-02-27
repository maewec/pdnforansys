<<<<<<< HEAD
# -*- coding: utf-8 -*-
"""
Набор для обработки Ansys
Версия от 2020.02.05 (исправлен макрос и обработка узлов вне диапазона)
"""

import os
import subprocess
import numpy as np

class WriteReadAnsysData:
    """Общий надкласс для чтения и записи данных Ansys
    ----
    Parameters:
        list_item - список требуемых параметрв в виде Item1_IT1NUM (см. Ansys
        Help, *GET для node)
        start_time - номер первого шага нагружения для чтения
        end_time - номер последнего шага нагружения (устанавливается диапазон
        между start_time и end_time)
        name_output - префикс названия выходных файлов макроса Ansys
        work_dir - рабочая директория проекта Ansys
        tmp_dir - временная директория для сохранения и чтения выходных файлов
        макроса Ansys"""

    def __init__(self, list_item, start_time, end_time=0, name_output='data',
                 work_dir='', tmp_dir=''):
        self.list_item = self.parse_item(list_item)  # список требуемых данных в Ansys
        self.set_time_range(start_time, end_time)  # список шагов
        self.name_output = name_output  # название выходных данных в макросе
        self.work_dir = work_dir
        self.tmp_dir = tmp_dir

    def set_item(self, list_item):
        """Установить новый набор требуемых параметров в виде списка Item1_IT1NUM
        для entity NODE (смотри справку Ansys) и преобразуется в список списков
        [Item1, IT1NUm]"""
        self.list_item = self.parse_item(list_item)

    def set_time_range(self, start_time, end_time=0):
        """Установить диапазон шагов или один шаг"""
        if end_time == 0:
            self.list_time = [start_time]
        else:
            self.list_time = [x for x in range(start_time, end_time + 1)]

    def set_add_time(self, start_time, end_time=0):
        """Добавить диапазон шагов или один шаг"""
        self.list_time = set(self.list_time)
        if end_time == 0:
            self.list_time.add(start_time)
            self.list_time = sorted(list(self.list_time))
        else:
            self.list_time.update({x for x in range(start_time, end_time + 1)})
            self.list_time = sorted(list(self.list_time))

    @staticmethod
    def parse_item(list_item):
        """Название требуемых параметров передается в виде списка Item1_IT1NUM
        для entity NODE (смотри справку Ansys) и преобразуется
        в список списков [Item1, IT1NUm]"""
        if type(list_item) == str:
            new_list_item = list_item.split(sep='_')
            if len(new_list_item) == 1:
                new_list_item.append('')
            return [new_list_item]
        else:
            new_list_item = []
            for i in list_item:
                i = i.split(sep='_')
                if len(i) == 1:
                    i.append('')
                new_list_item.append(i)
            return new_list_item


class FormMacrosAnsysData(WriteReadAnsysData):
    """Формирование макроса для записи результатов Ansys в текстовые файлы
    -----
    Parameters:
        list_item - список требуемых параметрв в виде Item1_IT1NUM (см. Ansys
        Help, *GET для node)
        start_time - номер первого шага нагружения для чтения
        end_time - номер последнего шага нагружения (устанавливается диапазон
        между start_time и end_time)
        list_namesel_el - список именованных наборов элементов
        list_namesel_node - список именованных наборов узлов
        list_nodes - список номеров узлов
        list_elems - список номеров элементов
        filerst - имя rst файла Ansys
        rsys - номер координатной системы для вывода
        name_output - префикс названия выходных файлов макроса Ansys
        name_file - название макроса для вывода параметров
        work_dir - рабочая директория проекта Ansys
        tmp_dir - временная директория для сохранения и чтения выходных файлов
        макроса Ansys"""

    def __init__(self, list_item, start_time, end_time=0, list_namesel_el=[],
                 list_namesel_node=[], list_nodes=[], list_elems=[],
                 filerst='file', rsys=0, name_output='data',
                 name_file='read_data.mac', work_dir='', tmp_dir=''):
        WriteReadAnsysData.__init__(self, list_item, start_time, end_time,
                                    name_output, work_dir, tmp_dir)
        self.name_file = name_file  # название макроса
        self.set_named_sel_el(list_namesel_el)  # список наборов элементов
        self.set_named_sel_node(list_namesel_node)  # список наборов узлов
        self.set_nodes(list_nodes)  # список номеров узлов
        self.set_elements(list_elems)  # список номеров элементов
        self.filerst = filerst  # название файла с результатами ansys
        self.rsys = rsys  # номер координатной системы

    def set_named_sel_el(self, *name_sel):
        """Установить именованные наборы элементов"""
        self.list_namesel_el = self.__multiset(name_sel)

    def set_named_sel_node(self, *name_sel):
        """Установить именованные наборы узлов"""
        self.list_namesel_node = self.__multiset(name_sel)

    def set_nodes(self, *nodes):
        """Установить номера узлов"""
        self.list_nodes = self.__multiset(nodes)

    def set_elements(self, *elems):
        """Установить номера элементов"""
        self.list_elems = self.__multiset(elems)

    @staticmethod
    def __multiset(name_sel):
        """Если первый аргумент в виде списка, то раскрываем его"""
        new_list = list(name_sel)
        if isinstance(new_list[0],
                      (list, tuple, set)):  # проверяем, являлся ли первый аргумент списком и раскрываем его
            new_list = list(new_list[0])
        return new_list

    def set_filerst(self, file):
        """Установить название файла результатов Ansys"""
        self.filerst = file

    def set_rsys(self, num):
        """Установить номер координатной системы"""
        self.rsys = num

    def __str__(self):
        return 'Набор данных: {0}\nШаги времени: {1}\nИменованный набор элементов: {2}\n\
Именованный набор узлов: {3}\nНабор номеров элементов: {4}\nНабор номеров узлов: {5}\n\
Имя файла: {6}\nИмя файла результатов Ansys: {7}\n\
Координатная система: {8}\nВременная директория: '.format(self.list_item, self.list_time,
                                                          self.list_namesel_el, self.list_namesel_node,
                                                          self.list_elems, self.list_nodes,
                                                          self.name_file, self.filerst, self.rsys,
                                                          self.tmp_dir)

    def form_macros(self):
        """Формирование тела макроса"""
        new_string = self.__head_string() + self.__nodeslist_full() + self.__named_string()
        new_string += self.__nodeslist_string() + self.__time_string()
        new_string += self.__body_string() + self.__end_string()
        return new_string

    def __head_string(self):
        """Голова макроса, включающая установку файла с результатами и
        координатной системы"""
        pattern = 'resu,\n/post1\n*dell,all\nfile,{0},rst\nrsys,{1}\nALLSEL,all\n'
        new_string = pattern.format(self.filerst, self.rsys)
        return new_string

    def __nodeslist_full(self):
        """Запись файла со всеми номерами узлов"""
        prefix = self.name_output
        if self.tmp_dir != '':
            prefix = '{0}/{1}'.format(self.tmp_dir, prefix)
        pattern_full = r"""*vget,nodes_list_full,node,,nlist
/out,{0}_nodeslist_full.tmp
*VWRITE,nodes_list_full(1)
(f16.0)
/out
ALLSEL,ALL
"""
        new_string = pattern_full.format(prefix)
        return new_string

    def __named_string(self):
        """Запись всех именованных наборов"""
        new_string = ''
        self.__flag_elem = False
        self.__flag_sel = 'S'

        for i, pattern in ((self.list_namesel_el, 'CMSEL,{0},{1}\n'),
                           (self.list_elems, 'ESEL,{0},ELEM,,{1}\n')):
            for k in i:
                new_string += self.__named_string_0(pattern, k)
                self.__flag_elem = True
        if self.__flag_elem:
            new_string += 'ALLSEL,BELOW,ELEM\n'
        for i, pattern in ((self.list_namesel_node, 'CMSEL,{0},{1}\n'),
                           (self.list_nodes, 'NSEL,{0},NODE,,{1}\n')):
            for k in i:
                new_string += self.__named_string_0(pattern, k)
        new_string += 'NSLE, R, CORNER\n'
        return new_string

    def __named_string_0(self, pattern, value):
        """В случае записи больше одного набора, для всех остальных выбирается
        опция добавления (A)"""
        new_string = pattern.format(self.__flag_sel, value)
        self.__flag_sel = 'A'
        return new_string

    def __nodeslist_string(self):
        """Если записаны наборы элементов или узлов, то записывается файл с
        номерами выбранных узлов"""
        prefix = self.name_output
        if self.tmp_dir != '':
            prefix = '{0}/{1}'.format(self.tmp_dir, prefix)
        pattern = r"""*vget,nodes_list,node,,nlist
/out,{0}_nodeslist.tmp
*VWRITE,nodes_list(1)
(f16.0)
/out
ALLSEL,ALL
"""
        new_string = ''
        if self.exist_named_sel():
            new_string = pattern.format(prefix)
        return new_string

    def exist_named_sel(self):
        """Проверка существования наборов узлов и элементов"""
        if self.list_namesel_el or self.list_namesel_node or self.list_elems or self.list_nodes:
            return True
        else:
            return False

    def __time_string(self):
        """Установка шагов расчета"""
        new_list_time = self.__list_time_new()
        new_string = ''
        pattern1 = 'start_{0} = {1}\nend_{2} = {3}\n'
        quant = len(new_list_time)
        for i in range(quant):
            new_string += pattern1.format(i + 1, new_list_time[i][0],
                                          i + 1, new_list_time[i][1])
        pattern2 = '*DO,k,1,{0}\n'
        new_string += pattern2.format(quant)
        text = '*DO,i,start_%k%,end_%k%\nset,i\n'
        new_string += text
        return new_string

    def __list_time_new(self):
        """Преобразование упорядоченного списка шагов в
        список списков диапазонов шагов
        Пример: [2, 3, 4, 8, 9, 18] --> [[2, 4], [8, 9], [18, 18]]"""
        new_list_time = []
        if len(self.list_time) == 1:
            new_list_time.append([self.list_time[0], self.list_time[0]])
        else:
            start = self.list_time[0]
            end = self.list_time[0]
            for i in self.list_time[1:]:
                if end + 1 != i:
                    new_list_time.append([start, end])
                    start = i
                    end = i
                else:
                    end = i
            else:
                new_list_time.append([start, end])
        return new_list_time

    def __body_string(self):
        """Формирование массивов выбранных параметров Ansys для записи"""
        new_string = ''
        pattern = '*vget,{0}_{1},node,,{0},{1},,,2\n'
        for i in self.list_item:
            new_string += pattern.format(i[0], i[1])
        pattern2 = '/OUT,{0}_{1}_{2}_%i%.tmp\n*VWRITE,{1}_{2}(1)\n(e15.7)\n/OUT\n'
        prefix = self.name_output
        if self.tmp_dir != '':
            prefix = '{0}/{1}'.format(self.tmp_dir, prefix)
        for i in self.list_item:
            new_string += pattern2.format(prefix, i[0], i[1])
        return new_string

    def __end_string(self):
        """Окончание макроса"""
        text = '*ENDDO\n*ENDDO\nFINISH\n/EXIT,NOSAVE'
        return text

    def save_macros(self, work_dir=''):
        """Сохранение подготовленного макроса"""
        if self.work_dir == '':
            self.work_dir = work_dir
        macros_body = self.form_macros()
        full_name = os.path.join(self.work_dir, self.name_file)
        with open(full_name, 'w') as macros_file:
            macros_file.write(macros_body)
        if self.tmp_dir != '':
            try:
                os.mkdir(os.path.join(self.work_dir, self.tmp_dir))
            except FileExistsError:
                pass


class ReadDataFromAnsys(FormMacrosAnsysData):
    """Чтение файлов результатов Ansys, подготовленных в классе FormMacrosAnsysData
    Формирвоание древоввидного словаря - Параметры - Шаги нагружения - Массив
    значений в узлах
    ----
    Parameters:
        list_item - список требуемых параметрв в виде Item1_IT1NUM (см. Ansys
        Help, *GET для node)
        start_time - номер первого шага нагружения для чтения
        end_time - номер последнего шага нагружения (устанавливается диапазон
        между start_time и end_time)
        exist_nodeslist - указание на чтение списка номеров узлов, если существует,
        то будут прочитаны параметры только для данных узлов
        name_output - префикс названия выходных файлов макроса Ansys
        work_dir - рабочая директория проекта Ansys
        tmp_dir - временная директория для сохранения и чтения выходных файлов
        макроса Ansys"""

    def __init__(self, list_item, start_time, end_time=0, exist_nodeslist=False,
                 name_output='data', work_dir='', tmp_dir=''):
        WriteReadAnsysData.__init__(self, list_item, start_time, end_time,
                                    name_output, work_dir, tmp_dir)
        self.exist_nodeslist = exist_nodeslist
        self.dict_res = dict()
        self.nodeslist = self.read_nodeslist(postfix='full')
        self.__index_full = self.nodeslist - 1
        if self.exist_nodeslist:                                                # если существуют наборы узлов/элементов, то добавляется индекс
            new_list = self.read_nodeslist()
            self.__index = self.index_numpy_array(self.nodeslist, new_list)
            self.nodeslist = new_list

    def read_nodeslist(self, postfix=''):
        """Чтение файла с номерами узлов"""
        if postfix == 'full':
            postfix = '_' + postfix
        filename = '{0}_nodeslist{1}.tmp'.format(self.name_output, postfix)
        with open(os.path.join(self.work_dir, self.tmp_dir, filename)) as src:
            l = src.read().splitlines()
            l = [int(float(item)) for item in l]
        return np.array(l)

    def get_dict_res(self):
        """Вывод полученного словаря результатов"""
        return self.dict_res

    def get_nodes_dict_res(self, *nodes):
        """Вывод полученного словаря результатов с выбранными узлами
        Parameters:
            *nodes - список узлов"""
        if isinstance(nodes[0], (list, tuple, np.ndarray)):  # проверяем, являлся ли первый аргумент списком и раскрываем его
            new_list = nodes[0]
        else:
            new_list = tuple(nodes,)
        index = self.index_numpy_array(self.nodeslist, new_list)  # индексы выбранных узлов
        new_dict = dict()
        for key_item in self.dict_res:
            new_dict[key_item] = dict()
            for key_time in self.dict_res[key_item]:
                new_dict[key_item][key_time] = self.dict_res[key_item][key_time][index]

        return new_dict

    @staticmethod
    def index_numpy_array(arr, val):
        """Возвращает индексы элементов val массиса arr"""
        index_arr = []
        if val is int:
            val = list((val,))
        k = 0
        i = 0
        i_max = len(val) - 1
        while k < len(arr):
            if val[i] == arr[k]:
                index_arr.append(k)
                i += 1
                if i > i_max:
                    break
                # проверка на возрастание узла из выборки, если не по возрастанию,
                # то счетчик k скидывается
                if i >= 1 and val[i-1] > val[i]:
                    k = -1
            k += 1
        if len(index_arr) - 1 < i_max:
            n = val[len(index_arr)-1]
            raise IndexError(f"Нет узла номер {n}")

        return np.array(index_arr, dtype=int)

    def form_dict_res(self):
        """Чтение файлов и формирование словаря результатов
        Формируется словарь параметров"""
        dict_1 = dict()
        for item in self.list_item:
            name_item = '{0}_{1}'.format(item[0], item[1])
            dict_1[name_item] = self.__form_dict_res_2(name_item)
        self.dict_res = dict_1

    def __form_dict_res_2(self, name_item):
        """Чтение файлов и формирование словаря результатов - 2
        Для каждого словаря параметров формируется словарь шагов нагружения"""
        dict_2 = dict()
        for time in self.list_time:
            filename = '{0}_{1}_{2}.tmp'.format(self.name_output, name_item, time)
            dict_2[time] = self.read_data_ansys(filename, float)
        return dict_2

    def read_data_ansys(self, filename, type_items=float):
        """Чтение файлов и формирование словаря результатов - 3
        Значения словаря шагов нагружения - массив данных numpy"""
        with open(os.path.join(self.work_dir, self.tmp_dir, filename)) as src:
            l = src.read().splitlines()
            l = [type_items(float(item)) for item in l]
        arr = np.array(l, type_items)
        arr = arr[self.__index_full]
        if self.exist_nodeslist:
            return arr[self.__index]
        else:
            return arr

    def __str__(self):
        return 'Набор данных: {0}\nШаги времени: {1}\nСуществование списка узлов: {2}\n\
Префикс выходного файла: {3}\nВременная директория: '.format(self.list_item, self.list_time,
                                                             self.exist_nodeslist, self.name_output, self.tmp_dir)

    def delete_data_file(self):
        """Удаление временных файлов, полученных макросом и загруженных в словарь"""
        for item in self.list_item:
            for time in self.list_time:
                filename = '{0}_{1}_{2}_{3}.tmp'.format(self.name_output,
                                                        item[0], item[1], time)
                full_path = os.path.join(self.work_dir, self.tmp_dir, filename)
                os.remove(full_path)
        if self.exist_nodeslist:
            filename = '{0}_nodeslist.tmp'.format(self.name_output)
            full_path = full_path = os.path.join(self.work_dir, self.tmp_dir,
                                                 filename)
            os.remove(full_path)


class RunAnsys:
    """Запуск макроса в Ansys
    ----
    Parameters:
        path_to_ansys - расположение исполняемого файла AnsysNNN.exe, где
        NNN - номер версии
        work_dir - рабочая директория с rst файлом Ansys
        name_macros - название файла макроса для запуска"""

    def __init__(self, path_to_ansys, work_dir, name_macros='read_data.mac',
                 flag_print=False):
        self.path_to_ansys = path_to_ansys
        self.work_dir = work_dir
        self.name_macros = name_macros
        self.flag_print = flag_print

    def run(self):
        full_name_macros = os.path.join(self.work_dir, self.name_macros)
        full_output = os.path.join(self.work_dir, 'file.out')
        pattern_command = '{0} -b -np 1 -dir {1} -i {2} -o {3}'
        full_command = pattern_command.format(self.path_to_ansys, self.work_dir,
                                              full_name_macros, full_output)
        if self.flag_print:
            print('Запуск Ansys по адресу:\n', self.path_to_ansys,
                  '\nВ рабочей директории:\n', self.work_dir)
        run_ansys = subprocess.run(full_command)
        if run_ansys.returncode == 0:
            if self.flag_print:
                print('Запуск Ansys завершился без ошибок')
            return True
        else:
            raise RuntimeError('Error running Ansys')

    def __str__(self):
        return 'Путь к Ansys: {0}\nРабочая директория: {1}\nНазвание макроса: {2}' \
            .format(self.path_to_ansys, self.work_dir, self.name_macros)


def form_table_title(text_table, columns=None, sep=None):
    """Формирование словаря, где ключи - первые элементы столбцов, а значения -
    массивы numpy остальных элементов столбцов
    Parameters:
        text_table - форматированная в виде таблицы строка с заголовками или
        путь к аналогично форматированному текстовому файлу
        columns - список ключей, если они не заданы в text_table
        sep - разделитель значений"""
    if '\n' not in text_table:
        if os.path.isfile(text_table):
            with open(text_table) as src:
                text_table = src.read()
        else:
            raise FileNotFoundError('text_table - не является таблицей и не является путем к файлу')
    body_list = []
    for line in text_table.splitlines():
        body_list.append(line.split(sep))
    if columns:
        if len(columns) != len(body_list[0]):
            raise ValueError('Число элементов списка columns не соответствует')
        head = columns
        body = body_list
    else:
        head = body_list[0]
        body = body_list[1:]
    return {head[i]: np.array(body, float).T[i] for i in range(len(head))}


def main():
    #    list_of_data_ansys = ('epel_x', 'epel_y', 'epel_z', 'epel_xy', 'epel_yz',
    #                          'epel_xz', 'eppl_x', 'eppl_y', 'eppl_z', 'eppl_xy',
    #                          'eppl_yz', 'eppl_xz', 's_x', 's_y', 's_z', 's_xy',
    #                          's_yz', 's_xz', 's_eqv', 's_1', 's_2', 's_3', 'temp')
    #    named_selection = ('disk_7', 'disk_8', 'disk_9', 'disk_lab')
    #    start_load_step =   2
    #    end_load_step =     2
    #    start_unload_step = 3
    #    end_unload_step =   5
    #    work_dir = r'g:\Nemtsev_ssd\mechanical\all_stendy'
    #
    #    b = FormMacrosAnsysData(list_of_data_ansys, start_load_step, end_load_step,
    #                            named_selection, path_save=work_dir)
    #    b.set_add_time(start_unload_step, end_unload_step)
    #    print(b)
    #    print(b.form_macros())
    # list_of_item = ('epel_x', 's_x', 's_eqv', 'bfe_temp')
    # named_selection = ('sel_2')
    # nam_sel_node = 'surf'
    # start_load_step = 2
    # end_load_step =2
    # start_unload_step = 4
    # end_unload_step = 5
    # work_dir = r'X:\prog\ansys'
    # path_ansys = r'C:\Program Files\ANSYS Inc\v150\ansys\bin\winx64\ANSYS150.exe'

    # one = FormMacrosAnsysData(list_of_item, start_load_step, end_load_step,
    #                           named_selection, list_namesel_node=nam_sel_node,
    #                           work_dir=work_dir, tmp_dir='')
    # one.set_add_time(start_unload_step, end_unload_step)
    # print(one)
    # one.save_macros()

    # RunAnsys(path_ansys, work_dir).run()

    # ansys_res = ReadDataFromAnsys(list_of_item, start_load_step, end_load_step,
    #                               exist_nodeslist=True, work_dir=work_dir,
    #                               tmp_dir='')
    # ansys_res.set_add_time(start_unload_step, end_unload_step)

    # ansys_res.form_dict_res()

    # res_dict = ansys_res.get_dict_res()

    # print(res_dict)

    # ansys_res.delete_data_file()

    list_of_item = ('epel_x', 's_x', 's_eqv', 'bfe_temp')
    start_load_step = 2
    namesel_el = ('krasota', 'ura')
    namesel_node = 'surf'
    work_dir = r'g:\work\python\ansys_manson_old\apdl'
    path_ansys = r'c:\Program Files\ANSYS Inc\v192\ansys\bin\winx64\ANSYS192.exe'
    res = FormMacrosAnsysData(list_of_item, start_load_step, work_dir=work_dir,
                        tmp_dir='tmp', list_namesel_el=namesel_el).form_macros()
    print(res)
#    RunAnsys(path_ansys, work_dir).run()
#    ansys_res = ReadDataFromAnsys(list_of_item, start_load_step, work_dir=work_dir,
#                                  tmp_dir='tmp')
#    ansys_res.form_dict_res()
#    res_dict = ansys_res.get_dict_res()

#    print(res_dict)


if __name__ == '__main__':
    main()
=======
# -*- coding: utf-8 -*-
"""
Набор для обработки Ansys
Версия от 2020.02.05 (исправлен макрос и обработка узлов вне диапазона)
"""

import os
import subprocess
import numpy as np

class WriteReadAnsysData:
    """Общий надкласс для чтения и записи данных Ansys
    ----
    Parameters:
        list_item - список требуемых параметрв в виде Item1_IT1NUM (см. Ansys
        Help, *GET для node)
        start_time - номер первого шага нагружения для чтения
        end_time - номер последнего шага нагружения (устанавливается диапазон
        между start_time и end_time)
        name_output - префикс названия выходных файлов макроса Ansys
        work_dir - рабочая директория проекта Ansys
        tmp_dir - временная директория для сохранения и чтения выходных файлов
        макроса Ansys"""

    def __init__(self, list_item, start_time, end_time=0, name_output='data',
                 work_dir='', tmp_dir=''):
        self.list_item = self.parse_item(list_item)  # список требуемых данных в Ansys
        self.set_time_range(start_time, end_time)  # список шагов
        self.name_output = name_output  # название выходных данных в макросе
        self.work_dir = work_dir
        self.tmp_dir = tmp_dir

    def set_item(self, list_item):
        """Установить новый набор требуемых параметров в виде списка Item1_IT1NUM
        для entity NODE (смотри справку Ansys) и преобразуется в список списков
        [Item1, IT1NUm]"""
        self.list_item = self.parse_item(list_item)

    def set_time_range(self, start_time, end_time=0):
        """Установить диапазон шагов или один шаг"""
        if end_time == 0:
            self.list_time = [start_time]
        else:
            self.list_time = [x for x in range(start_time, end_time + 1)]

    def set_add_time(self, start_time, end_time=0):
        """Добавить диапазон шагов или один шаг"""
        self.list_time = set(self.list_time)
        if end_time == 0:
            self.list_time.add(start_time)
            self.list_time = sorted(list(self.list_time))
        else:
            self.list_time.update({x for x in range(start_time, end_time + 1)})
            self.list_time = sorted(list(self.list_time))

    @staticmethod
    def parse_item(list_item):
        """Название требуемых параметров передается в виде списка Item1_IT1NUM
        для entity NODE (смотри справку Ansys) и преобразуется
        в список списков [Item1, IT1NUm]"""
        if type(list_item) == str:
            new_list_item = list_item.split(sep='_')
            if len(new_list_item) == 1:
                new_list_item.append('')
            return [new_list_item]
        else:
            new_list_item = []
            for i in list_item:
                i = i.split(sep='_')
                if len(i) == 1:
                    i.append('')
                new_list_item.append(i)
            return new_list_item


class FormMacrosAnsysData(WriteReadAnsysData):
    """Формирование макроса для записи результатов Ansys в текстовые файлы
    -----
    Parameters:
        list_item - список требуемых параметрв в виде Item1_IT1NUM (см. Ansys
        Help, *GET для node)
        start_time - номер первого шага нагружения для чтения
        end_time - номер последнего шага нагружения (устанавливается диапазон
        между start_time и end_time)
        list_namesel_el - список именованных наборов элементов
        list_namesel_node - список именованных наборов узлов
        list_nodes - список номеров узлов
        list_elems - список номеров элементов
        filerst - имя rst файла Ansys
        rsys - номер координатной системы для вывода
        name_output - префикс названия выходных файлов макроса Ansys
        name_file - название макроса для вывода параметров
        work_dir - рабочая директория проекта Ansys
        tmp_dir - временная директория для сохранения и чтения выходных файлов
        макроса Ansys"""

    def __init__(self, list_item, start_time, end_time=0, list_namesel_el=[],
                 list_namesel_node=[], list_nodes=[], list_elems=[],
                 filerst='file', rsys=0, name_output='data',
                 name_file='read_data.mac', work_dir='', tmp_dir=''):
        WriteReadAnsysData.__init__(self, list_item, start_time, end_time,
                                    name_output, work_dir, tmp_dir)
        self.name_file = name_file  # название макроса
        self.set_named_sel_el(list_namesel_el)  # список наборов элементов
        self.set_named_sel_node(list_namesel_node)  # список наборов узлов
        self.set_nodes(list_nodes)  # список номеров узлов
        self.set_elements(list_elems)  # список номеров элементов
        self.filerst = filerst  # название файла с результатами ansys
        self.rsys = rsys  # номер координатной системы

    def set_named_sel_el(self, *name_sel):
        """Установить именованные наборы элементов"""
        self.list_namesel_el = self.__multiset(name_sel)

    def set_named_sel_node(self, *name_sel):
        """Установить именованные наборы узлов"""
        self.list_namesel_node = self.__multiset(name_sel)

    def set_nodes(self, *nodes):
        """Установить номера узлов"""
        self.list_nodes = self.__multiset(nodes)

    def set_elements(self, *elems):
        """Установить номера элементов"""
        self.list_elems = self.__multiset(elems)

    @staticmethod
    def __multiset(name_sel):
        """Если первый аргумент в виде списка, то раскрываем его"""
        new_list = list(name_sel)
        if isinstance(new_list[0],
                      (list, tuple, set)):  # проверяем, являлся ли первый аргумент списком и раскрываем его
            new_list = list(new_list[0])
        return new_list

    def set_filerst(self, file):
        """Установить название файла результатов Ansys"""
        self.filerst = file

    def set_rsys(self, num):
        """Установить номер координатной системы"""
        self.rsys = num

    def __str__(self):
        return 'Набор данных: {0}\nШаги времени: {1}\nИменованный набор элементов: {2}\n\
Именованный набор узлов: {3}\nНабор номеров элементов: {4}\nНабор номеров узлов: {5}\n\
Имя файла: {6}\nИмя файла результатов Ansys: {7}\n\
Координатная система: {8}\nВременная директория: '.format(self.list_item, self.list_time,
                                                          self.list_namesel_el, self.list_namesel_node,
                                                          self.list_elems, self.list_nodes,
                                                          self.name_file, self.filerst, self.rsys,
                                                          self.tmp_dir)

    def form_macros(self):
        """Формирование тела макроса"""
        new_string = self.__head_string() + self.__nodeslist_full() + self.__named_string()
        new_string += self.__nodeslist_string() + self.__time_string()
        new_string += self.__body_string() + self.__end_string()
        return new_string

    def __head_string(self):
        """Голова макроса, включающая установку файла с результатами и
        координатной системы"""
        pattern = 'resu,\n/post1\n*dell,all\nfile,{0},rst\nrsys,{1}\nALLSEL,all\n'
        new_string = pattern.format(self.filerst, self.rsys)
        return new_string

    def __nodeslist_full(self):
        """Запись файла со всеми номерами узлов"""
        prefix = self.name_output
        if self.tmp_dir != '':
            prefix = '{0}/{1}'.format(self.tmp_dir, prefix)
        pattern_full = r"""*vget,nodes_list_full,node,,nlist
/out,{0}_nodeslist_full.tmp
*VWRITE,nodes_list_full(1)
(f16.0)
/out
ALLSEL,ALL
"""
        new_string = pattern_full.format(prefix)
        return new_string

    def __named_string(self):
        """Запись всех именованных наборов"""
        new_string = ''
        self.__flag_elem = False
        self.__flag_sel = 'S'

        for i, pattern in ((self.list_namesel_el, 'CMSEL,{0},{1}\n'),
                           (self.list_elems, 'ESEL,{0},ELEM,,{1}\n')):
            for k in i:
                new_string += self.__named_string_0(pattern, k)
                self.__flag_elem = True
        if self.__flag_elem:
            new_string += 'ALLSEL,BELOW,ELEM\n'
        for i, pattern in ((self.list_namesel_node, 'CMSEL,{0},{1}\n'),
                           (self.list_nodes, 'NSEL,{0},NODE,,{1}\n')):
            for k in i:
                new_string += self.__named_string_0(pattern, k)
        new_string += 'NSLE, R, CORNER\n'
        return new_string

    def __named_string_0(self, pattern, value):
        """В случае записи больше одного набора, для всех остальных выбирается
        опция добавления (A)"""
        new_string = pattern.format(self.__flag_sel, value)
        self.__flag_sel = 'A'
        return new_string

    def __nodeslist_string(self):
        """Если записаны наборы элементов или узлов, то записывается файл с
        номерами выбранных узлов"""
        prefix = self.name_output
        if self.tmp_dir != '':
            prefix = '{0}/{1}'.format(self.tmp_dir, prefix)
        pattern = r"""*vget,nodes_list,node,,nlist
/out,{0}_nodeslist.tmp
*VWRITE,nodes_list(1)
(f16.0)
/out
ALLSEL,ALL
"""
        new_string = ''
        if self.exist_named_sel():
            new_string = pattern.format(prefix)
        return new_string

    def exist_named_sel(self):
        """Проверка существования наборов узлов и элементов"""
        if self.list_namesel_el or self.list_namesel_node or self.list_elems or self.list_nodes:
            return True
        else:
            return False

    def __time_string(self):
        """Установка шагов расчета"""
        new_list_time = self.__list_time_new()
        new_string = ''
        pattern1 = 'start_{0} = {1}\nend_{2} = {3}\n'
        quant = len(new_list_time)
        for i in range(quant):
            new_string += pattern1.format(i + 1, new_list_time[i][0],
                                          i + 1, new_list_time[i][1])
        pattern2 = '*DO,k,1,{0}\n'
        new_string += pattern2.format(quant)
        text = '*DO,i,start_%k%,end_%k%\nset,i\n'
        new_string += text
        return new_string

    def __list_time_new(self):
        """Преобразование упорядоченного списка шагов в
        список списков диапазонов шагов
        Пример: [2, 3, 4, 8, 9, 18] --> [[2, 4], [8, 9], [18, 18]]"""
        new_list_time = []
        if len(self.list_time) == 1:
            new_list_time.append([self.list_time[0], self.list_time[0]])
        else:
            start = self.list_time[0]
            end = self.list_time[0]
            for i in self.list_time[1:]:
                if end + 1 != i:
                    new_list_time.append([start, end])
                    start = i
                    end = i
                else:
                    end = i
            else:
                new_list_time.append([start, end])
        return new_list_time

    def __body_string(self):
        """Формирование массивов выбранных параметров Ansys для записи"""
        new_string = ''
        pattern = '*vget,{0}_{1},node,,{0},{1},,,2\n'
        for i in self.list_item:
            new_string += pattern.format(i[0], i[1])
        pattern2 = '/OUT,{0}_{1}_{2}_%i%.tmp\n*VWRITE,{1}_{2}(1)\n(e15.7)\n/OUT\n'
        prefix = self.name_output
        if self.tmp_dir != '':
            prefix = '{0}/{1}'.format(self.tmp_dir, prefix)
        for i in self.list_item:
            new_string += pattern2.format(prefix, i[0], i[1])
        return new_string

    def __end_string(self):
        """Окончание макроса"""
        text = '*ENDDO\n*ENDDO\nFINISH\n/EXIT,NOSAVE'
        return text

    def save_macros(self, work_dir=''):
        """Сохранение подготовленного макроса"""
        if self.work_dir == '':
            self.work_dir = work_dir
        macros_body = self.form_macros()
        full_name = os.path.join(self.work_dir, self.name_file)
        with open(full_name, 'w') as macros_file:
            macros_file.write(macros_body)
        if self.tmp_dir != '':
            try:
                os.mkdir(os.path.join(self.work_dir, self.tmp_dir))
            except FileExistsError:
                pass


class ReadDataFromAnsys(FormMacrosAnsysData):
    """Чтение файлов результатов Ansys, подготовленных в классе FormMacrosAnsysData
    Формирвоание древоввидного словаря - Параметры - Шаги нагружения - Массив
    значений в узлах
    ----
    Parameters:
        list_item - список требуемых параметрв в виде Item1_IT1NUM (см. Ansys
        Help, *GET для node)
        start_time - номер первого шага нагружения для чтения
        end_time - номер последнего шага нагружения (устанавливается диапазон
        между start_time и end_time)
        exist_nodeslist - указание на чтение списка номеров узлов, если существует,
        то будут прочитаны параметры только для данных узлов
        name_output - префикс названия выходных файлов макроса Ansys
        work_dir - рабочая директория проекта Ansys
        tmp_dir - временная директория для сохранения и чтения выходных файлов
        макроса Ansys"""

    def __init__(self, list_item, start_time, end_time=0, exist_nodeslist=False,
                 name_output='data', work_dir='', tmp_dir=''):
        WriteReadAnsysData.__init__(self, list_item, start_time, end_time,
                                    name_output, work_dir, tmp_dir)
        self.exist_nodeslist = exist_nodeslist
        self.dict_res = dict()
        self.nodeslist = self.read_nodeslist(postfix='full')
        flag = True                                                             # проверка, списка узлов на непрерывное возрастание на 1 от нуля
        for i in self.nodeslist:
            if self.nodeslist[i-1] != i:
                flag = False
                break
        if self.exist_nodeslist:                                                # если существуют наборы узлов/элементов, то добавляется индекс
            new_list = self.read_nodeslist()
            if flag:                                                            # быстрое вычисление индекса
                self.__index = new_list - 1
            else:                                                               # медленное вычисление индекса
                self.__index = self.index_numpy_array(self.nodeslist, new_list)
            self.nodeslist = new_list

    def read_nodeslist(self, postfix=''):
        """Чтение файла с номерами узлов"""
        if postfix == 'full':
            postfix = '_' + postfix
        filename = '{0}_nodeslist{1}.tmp'.format(self.name_output, postfix)
        with open(os.path.join(self.work_dir, self.tmp_dir, filename)) as src:
            l = src.read().splitlines()
            l = [int(float(item)) for item in l]
        return np.array(l)

    def get_dict_res(self):
        """Вывод полученного словаря результатов"""
        return self.dict_res

    def get_nodes_dict_res(self, *nodes):
        """Вывод полученного словаря результатов с выбранными узлами
        Parameters:
            *nodes - список узлов"""
        if isinstance(nodes[0], (list, tuple, np.ndarray)):  # проверяем, являлся ли первый аргумент списком и раскрываем его
            new_list = nodes[0]
        else:
            new_list = tuple(nodes,)
        index = self.index_numpy_array(self.nodeslist, new_list)  # индексы выбранных узлов
        new_dict = dict()
        for key_item in self.dict_res:
            new_dict[key_item] = dict()
            for key_time in self.dict_res[key_item]:
                new_dict[key_item][key_time] = self.dict_res[key_item][key_time][index]

        return new_dict

    @staticmethod
    def index_numpy_array(arr, val):
        """Возвращает индексы элементов val массиса arr"""
        index_arr = np.zeros(len(val), dtype=int)
        if val is int:
            val = list((val,))
        if isinstance(val, (list, tuple, np.ndarray)):
            k = 0
            for i in val:
                if i % 10000 == 0:
                    print(i)
                try:
                    index_arr[k] = np.where(i == arr)[0][0]
                    k += 1
                except IndexError:
                    raise IndexError('Узла {0} не существует'.format(i))
        else:
            raise ValueError('val должен быть int или списком int')
        return index_arr

    def form_dict_res(self):
        """Чтение файлов и формирование словаря результатов
        Формируется словарь параметров"""
        dict_1 = dict()
        for item in self.list_item:
            name_item = '{0}_{1}'.format(item[0], item[1])
            dict_1[name_item] = self.__form_dict_res_2(name_item)
        self.dict_res = dict_1

    def __form_dict_res_2(self, name_item):
        """Чтение файлов и формирование словаря результатов - 2
        Для каждого словаря параметров формируется словарь шагов нагружения"""
        dict_2 = dict()
        for time in self.list_time:
            filename = '{0}_{1}_{2}.tmp'.format(self.name_output, name_item, time)
            dict_2[time] = self.read_data_ansys(filename, float)
        return dict_2

    def read_data_ansys(self, filename, type_items=float):
        """Чтение файлов и формирование словаря результатов - 3
        Значения словаря шагов нагружения - массив данных numpy"""
        with open(os.path.join(self.work_dir, self.tmp_dir, filename)) as src:
            l = src.read().splitlines()
            l = [type_items(float(item)) for item in l]
        arr = np.array(l, type_items)
        if self.exist_nodeslist:
            return arr[self.__index]
        else:
            return arr

    def __str__(self):
        return 'Набор данных: {0}\nШаги времени: {1}\nСуществование списка узлов: {2}\n\
Префикс выходного файла: {3}\nВременная директория: '.format(self.list_item, self.list_time,
                                                             self.exist_nodeslist, self.name_output, self.tmp_dir)

    def delete_data_file(self):
        """Удаление временных файлов, полученных макросом и загруженных в словарь"""
        for item in self.list_item:
            for time in self.list_time:
                filename = '{0}_{1}_{2}_{3}.tmp'.format(self.name_output,
                                                        item[0], item[1], time)
                full_path = os.path.join(self.work_dir, self.tmp_dir, filename)
                os.remove(full_path)
        if self.exist_nodeslist:
            filename = '{0}_nodeslist.tmp'.format(self.name_output)
            full_path = full_path = os.path.join(self.work_dir, self.tmp_dir,
                                                 filename)
            os.remove(full_path)


class RunAnsys:
    """Запуск макроса в Ansys
    ----
    Parameters:
        path_to_ansys - расположение исполняемого файла AnsysNNN.exe, где
        NNN - номер версии
        work_dir - рабочая директория с rst файлом Ansys
        name_macros - название файла макроса для запуска"""

    def __init__(self, path_to_ansys, work_dir, name_macros='read_data.mac',
                 flag_print=False):
        self.path_to_ansys = path_to_ansys
        self.work_dir = work_dir
        self.name_macros = name_macros
        self.flag_print = flag_print

    def run(self):
        full_name_macros = os.path.join(self.work_dir, self.name_macros)
        full_output = os.path.join(self.work_dir, 'file.out')
        pattern_command = '{0} -b -np 1 -dir {1} -i {2} -o {3}'
        full_command = pattern_command.format(self.path_to_ansys, self.work_dir,
                                              full_name_macros, full_output)
        if self.flag_print:
            print('Запуск Ansys по адресу:\n', self.path_to_ansys,
                  '\nВ рабочей директории:\n', self.work_dir)
        run_ansys = subprocess.run(full_command)
        if run_ansys.returncode == 0:
            if self.flag_print:
                print('Запуск Ansys завершился без ошибок')
            return True
        else:
            raise RuntimeError('Error running Ansys')

    def __str__(self):
        return 'Путь к Ansys: {0}\nРабочая директория: {1}\nНазвание макроса: {2}' \
            .format(self.path_to_ansys, self.work_dir, self.name_macros)


def form_table_title(text_table, columns=None, sep=None):
    """Формирование словаря, где ключи - первые элементы столбцов, а значения -
    массивы numpy остальных элементов столбцов
    Parameters:
        text_table - форматированная в виде таблицы строка с заголовками или
        путь к аналогично форматированному текстовому файлу
        columns - список ключей, если они не заданы в text_table
        sep - разделитель значений"""
    if '\n' not in text_table:
        if os.path.isfile(text_table):
            with open(text_table) as src:
                text_table = src.read()
        else:
            raise FileNotFoundError('text_table - не является таблицей и не является путем к файлу')
    body_list = []
    for line in text_table.splitlines():
        body_list.append(line.split(sep))
    if columns:
        if len(columns) != len(body_list[0]):
            raise ValueError('Число элементов списка columns не соответствует')
        head = columns
        body = body_list
    else:
        head = body_list[0]
        body = body_list[1:]
    return {head[i]: np.array(body, float).T[i] for i in range(len(head))}


def main():
    #    list_of_data_ansys = ('epel_x', 'epel_y', 'epel_z', 'epel_xy', 'epel_yz',
    #                          'epel_xz', 'eppl_x', 'eppl_y', 'eppl_z', 'eppl_xy',
    #                          'eppl_yz', 'eppl_xz', 's_x', 's_y', 's_z', 's_xy',
    #                          's_yz', 's_xz', 's_eqv', 's_1', 's_2', 's_3', 'temp')
    #    named_selection = ('disk_7', 'disk_8', 'disk_9', 'disk_lab')
    #    start_load_step =   2
    #    end_load_step =     2
    #    start_unload_step = 3
    #    end_unload_step =   5
    #    work_dir = r'g:\Nemtsev_ssd\mechanical\all_stendy'
    #
    #    b = FormMacrosAnsysData(list_of_data_ansys, start_load_step, end_load_step,
    #                            named_selection, path_save=work_dir)
    #    b.set_add_time(start_unload_step, end_unload_step)
    #    print(b)
    #    print(b.form_macros())
    # list_of_item = ('epel_x', 's_x', 's_eqv', 'bfe_temp')
    # named_selection = ('sel_2')
    # nam_sel_node = 'surf'
    # start_load_step = 2
    # end_load_step =2
    # start_unload_step = 4
    # end_unload_step = 5
    # work_dir = r'X:\prog\ansys'
    # path_ansys = r'C:\Program Files\ANSYS Inc\v150\ansys\bin\winx64\ANSYS150.exe'

    # one = FormMacrosAnsysData(list_of_item, start_load_step, end_load_step,
    #                           named_selection, list_namesel_node=nam_sel_node,
    #                           work_dir=work_dir, tmp_dir='')
    # one.set_add_time(start_unload_step, end_unload_step)
    # print(one)
    # one.save_macros()

    # RunAnsys(path_ansys, work_dir).run()

    # ansys_res = ReadDataFromAnsys(list_of_item, start_load_step, end_load_step,
    #                               exist_nodeslist=True, work_dir=work_dir,
    #                               tmp_dir='')
    # ansys_res.set_add_time(start_unload_step, end_unload_step)

    # ansys_res.form_dict_res()

    # res_dict = ansys_res.get_dict_res()

    # print(res_dict)

    # ansys_res.delete_data_file()

    list_of_item = ('epel_x', 's_x', 's_eqv', 'bfe_temp')
    start_load_step = 2
    namesel_el = ('krasota', 'ura')
    namesel_node = 'surf'
    work_dir = r'g:\work\python\ansys_manson_old\apdl'
    path_ansys = r'c:\Program Files\ANSYS Inc\v192\ansys\bin\winx64\ANSYS192.exe'
    res = FormMacrosAnsysData(list_of_item, start_load_step, work_dir=work_dir,
                        tmp_dir='tmp', list_namesel_el=namesel_el).form_macros()
    print(res)
#    RunAnsys(path_ansys, work_dir).run()
#    ansys_res = ReadDataFromAnsys(list_of_item, start_load_step, work_dir=work_dir,
#                                  tmp_dir='tmp')
#    ansys_res.form_dict_res()
#    res_dict = ansys_res.get_dict_res()

#    print(res_dict)


if __name__ == '__main__':
    main()
>>>>>>> 1cefc16ffc7bffc8455dae9bdc989fdd75a1956a
