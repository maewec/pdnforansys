# pdnforansys

## Введение
Пакет для чтения результатов прочностного расчета Ansys (полученных в виде .rst файла) и последующей загрузкой этих результатов в python в виде словаря. 

## Описание
С помощью пакета возможно получить результаты расчета в узлах (возможно выбрать узлы по номерам узлов, элементов, названиям наборов узлов и элементов) на одном или нескольких шагах нагружения.
В python результаты представлены в виде одномерного массива данных по выбранным узлам, которые расположены в двухуровневом словаре с ключом вида результатов на первом уровне и с ключом времени нагружения на втором (res_dict[item][time])

## Пример использования

	from pdnforansys import foransys
	
	work_dir = r'path/to/ansys/result'
	list_item = ['bfe_temp', 's_eqv']
	start_time = 1
	end_time = 2
	list_namesel_el = ['component1', 'component2']
	form = foransys.FormMacrosAnsysData(list_item, start_time, end_time,
										list_namesel_el=namesel_el,
										work_dir=work_dir)
	form.save_macros()

	path_ansys = r'path/to/ansys/bin/winx64/ansysXXX.exe'
	foransys.RunAnsys(path_ansys, work_dir).run()
	
	ansys_res = foransys.ReadDataFromAnsys(list_item, start_time, end_time,
										   exist_nodelist=True, work_dir=work_dir)
	ansys_res.form_dict_res()
	res1, node_dict, time_dict = ansys_res.get_item_node_time(ansys_res.nodeslist)

	# Получить температуру у узла 1 на шаге 1
	node = 1
	temp = 500
	time = 1
	value = res1['bfe_temp'][node_dict[node]][time_dict[time]]

