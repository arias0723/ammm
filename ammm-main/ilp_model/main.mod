main {
	// Creation of the model and importing data for the model
	var src = new IloOplModelSource("project.1.mod");
	var def = new IloOplModelDefinition(src);
	var cplex = new IloCplex();
	var model = new IloOplModel(def,cplex);
	var data = new IloOplDataSource("04_big.dat");
	model.addDataSource(data);
	model.generate();
	
	var start = new Date();
	var start_time = start.getTime();
	
//	cplex.epgap=0.01;
	
	// POSTPROCESSING AND SOLUTION
	if(cplex.solve()) {
		writeln("OBJECTIVE: " + cplex.getObjValue());
		writeln();
//		write("PATH: 0 -> ")
//		for (var i in model.nodes){
//        	for (var j in model.nodes){
//            	if (model.x[i][j] != 0) {
//              		write(j, " -> ");
//				}		
//			}		
//		}
//	writeln("0");
	writeln();
	}	
	else{
		writeln("No solution found");	  
	}
	
	var end = new Date();
	var end_time = end.getTime();
	write("Time:", end_time - start_time);
	write
};