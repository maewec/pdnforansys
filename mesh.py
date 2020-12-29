# -*- coding: utf-8 -*-
import numpy as np
import re
import os

pattern = r'''
^
\s{0,7}(\d{1,8})
\s+\d+
\s+\d+
\s+\d+
\s+\d+
\s+\d+
((\s+\d{1,7})+)
'''
pattern = re.compile(pattern, re.VERBOSE)

pattern2 = r'''
^
\s{36}
((\s*\d{1,7})+)
'''
pattern2 = re.compile(pattern2, re.VERBOSE)

class MeshFromElist:

    def __init__(self, path):

        self.path = path
        self.elem_list = None
        self.node_list = None
        self.ndel_list = None

    pattern = r'''
    ^
    \s{0,7}(\d{1,8})
    \s+\d+
    \s+\d+
    \s+\d+
    \s+\d+
    \s+\d+
    ((\s+\d{1,7})+)
    '''
    pattern = re.compile(pattern, re.VERBOSE)

    pattern2 = r'''
    ^
    \s{36}
    ((\s*\d{1,7})+)
    '''
    pattern2 = re.compile(pattern2, re.VERBOSE)

    def read(self):

        self.elem_list = np.zeros(10000000, dtype=int)
        self.node_list = np.zeros(10000000, dtype=int)
        self.ndel_list = np.zeros((10000000, 2), dtype=int)

        k_e = 0
        k_n = 0
        k_ne = 0
        flag = False
        with open(self.path) as src:
            for line in src:
                search = MeshFromElist.pattern.search(line)
                if search:
                    pars = search.groups()
                    elem = int(pars[0])
                    self.elem_list[k_e] = elem
                    k_e += 1
                    nodes = [int(n) for n in pars[1].split()]
                    for node in nodes:
                        if not node in self.node_list:
                            self.node_list[k_n] = node
                            k_n += 1
                        self.ndel_list[k_ne][0] = elem
                        self.ndel_list[k_ne][1] = node
                        k_ne +=1
                    flag = True
                elif flag:
                    search = MeshFromElist.pattern2.search(line)
                    if search:
                        pars = search.groups()
                        nodes = [int(n) for n in pars[0].split()]
                        for node in nodes:
                            if not node in self.node_list:
                                self.node_list[k_n] = node
                                k_n += 1
                            self.ndel_list[k_ne][0] = elem
                            self.ndel_list[k_ne][1] = node
                            k_ne +=1

        self.elem_list = np.array(self.elem_list)
        self.node_list = np.array(self.node_list)
        self.node_list.sort()
        self.ndel_list = np.array(self.ndel_list)
        self.ndel_list = self.ndel_list[self.ndel_list[:,0].argsort()]

    def get_elems(self):
        """Получить массив номеров элементов"""
        return self.elem_list

    def get_nodes(self):
        """Получить массив номеров узлов"""
        return self.node_list

    def get_elems_and_nodes(self):
        """Получить двумерный массив элементов и принадлежащих им узлов"""
        return self.ndel_list

    def get_all(self):
        return self.elem_list, self.node_list, self.ndel_list

def main():
    work_dir = r'h:\Nemtsev\work\117\NDS\KVD\result\m3_natyag2_polet\or_10'
    data_file = 'elist.dat'
    os.chdir(work_dir)

    global elem_list, node_list, ndel_list

    mesh = MeshFromElist(data_file)
    mesh.read()
    elem_list, node_list, ndel_list = mesh.get_all()



if __name__ == '__main__':
    main()