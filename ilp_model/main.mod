main {
  // Creation of the model and importing data for the model
  var src = new IloOplModelSource("project.1.mod");
  var def = new IloOplModelDefinition(src);
  var cplex = new IloCplex();
  var model = new IloOplModel(def, cplex);
  var data = new IloOplDataSource("input.dat");
  model.addDataSource(data);
  model.generate();

  var start = new Date();
  var start_time = start.getTime();

  // Return a solution if it is within 1% of the optimal bound
  // cplex.epgap=0.01;
  // cplex.workmem=6000;
  // cplex.nodefileind=3;
  // cplex.threads=4;
  // Set a time limit (e.g., 3600 seconds = 1 hour)
  // cplex.tilim=3600;
  // cplex.varsel=3;

  // POSTPROCESSING AND SOLUTION
  if (cplex.solve()) {
    model.postProcess();
  } else {
    writeln("No solution found");
  }

  var end = new Date();
  var end_time = end.getTime();
  write("Time:", end_time - start_time);
}
