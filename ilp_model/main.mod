main {
	// Creation of the model and importing data for the model
	var src = new IloOplModelSource("project.1.mod");
	var def = new IloOplModelDefinition(src);
	var cplex = new IloCplex();
	var model = new IloOplModel(def,cplex);
	var data = new IloOplDataSource("input.dat");
	model.addDataSource(data);
	model.generate();
	
	var start = new Date();
	var start_time = start.getTime();
	

  // limit memory used by CPLEX (MB)
  // cplex.workmem = 2048;    // set to available RAM, e.g. 2048 = 2GB
  // stop after 1800 seconds (30 minutes)
  // cplex.tilim = 1800;

  // allow a small optimality gap so solver returns earlier
  //cplex.epgap = 0.01;      // stop when relative MIP gap <= 1%

  // use multiple threads if you want (or set to 1 to be conservative)
  // cplex.threads = 2;

  // re-enable presolve / aggregator if you had turned them off
  //cplex.preind = 1;
  //cplex.aggind = 1;
  // optional: limit nodes to bound runtime
  // cplex.mip.limits.nodes = 100000;
	
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