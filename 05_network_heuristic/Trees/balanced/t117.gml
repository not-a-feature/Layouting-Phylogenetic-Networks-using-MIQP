graph [
	comment "Rooted network with node coordinates"
	directed 1
	id 1
	label "Graph" 
	node [
		id 0
		label 0
		x "0"
		y "0"
	]
	node [
		id 1
		label 1
		x "1"
		y "0"
	]
	node [
		id 2
		label 2
		x "1"
		y "0"
	]
	node [
		id 3
		label 3
		x "1"
		y "0"
	]
	node [
		id 4
		label 4
		x "2"
		y "0"
	]
	node [
		id 5
		label 5
		x "2"
		y "0"
	]
	edge [
		source 0
		target 1
	]
	edge [
		source 1
		target 5
		hybrid 1
	]
	edge [
		source 3
		target 2
		hybrid 1
	]
	edge [
		source 0
		target 3
	]
	edge [
		source 0
		target 2
		hybrid 1
	]
	edge [
		source 1
		target 4
	]
	edge [
		source 0
		target 5
		hybrid 1
	]

]