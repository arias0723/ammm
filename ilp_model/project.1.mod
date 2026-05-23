// ** PLEASE ONLY CHANGE THIS FILE WHERE INDICATED **
// In particular, do not change the names of the OPL variables.

int n 	          = ...;
int m 	          = ...;
int w[1..m] 	  = ...;
int c[1..m] 	  = ...;
int t[1..n][1..n] = ...;

// Define here your decision variables and
// any other auxiliary OPL variables you need.
// You can run an execute block if needed.

//>>>>>>>>>>>>>>>>

range B = 1..n;					// Bases
range S = 1..m;					// Specialists

tuple Edge {
  int i;
  int j;
}
// There exist an edge from base i to j
// Leverage tuple definition to avoid extra constraints in the model
{Edge} E = {<i,j> | i in B, j in B : i < j && t[i][j] > 0};

dvar boolean x[S][E];   		// specialist s assigned to edge e
dvar boolean d[E];      		// edge e is destroyed or not
dvar boolean g[B];      		// base b belongs to group g {0,1}

//<<<<<<<<<<<<<<<<

// You can run an execute block if needed.

execute {

//>>>>>>>>>>>>>>>>

//<<<<<<<<<<<<<<<<
}

minimize  // Write here the objective function.

//>>>>>>>>>>>>>>>>

	sum(s in S, e in E) c[s] * x[s][e];

//<<<<<<<<<<<<<<<<

subject to {

    // Write here the constraints.

    //>>>>>>>>>>>>>>>>
    
  	// Each specialist assigned to at most one pipe
  	forall(s in S)
    	sum(e in E) x[s][e] <= 1;

  	// Destroyed pipe enough total hours
  	forall(e in E)
    	sum(s in S) w[s] * x[s][e] >= t[e.i][e.j] * d[e];

  	// Specialists only assigned to targeted pipes
  	forall(s in S, e in E)
    	x[s][e] <= d[e];

  	// Pipe e destroyed -> Bases (i,j) belong to different groups
  	forall(e in E) {
    	d[e] >= g[e.i] - g[e.j];
    	d[e] >= g[e.j] - g[e.i];
  	}

  	// Graph is disconected (1 <= # of groups <= n-1)
  	sum(i in B) g[i] >= 1;
  	sum(i in B) g[i] <= n - 1;

    //<<<<<<<<<<<<<<<<
}

// You can run an execute block if needed.

execute {

//>>>>>>>>>>>>>>>>

  writeln("Total cost: ", cplex.getObjValue());
  writeln();
  for (var e in E) {
    if (d[e] == 1) {
      write("Destroy pipe {", e.i, ",", e.j, "} with specialists:");
      for (var s in S) {
        if (x[s][e] == 1) write(" ", s);
      }
      writeln();
    }
  }
  writeln();

  write("Partition S0 = {");
  var first = true;
  for (var i in B) {
    if (g[i] == 0) {
      if (!first) write(",");
      write(i);
      first = false;
    }
  }
  writeln("}");
    
  write("Partition S1 = {");
  var first = true;
  for (var i in B) {
    if (g[i] == 1) {
      if (!first) write(",");
      write(i);
      first = false;
    }
  }
  writeln("}");
  writeln();

//<<<<<<<<<<<<<<<<
}
