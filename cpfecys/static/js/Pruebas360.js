//RMGB: Código de javascript para generar las gráficas de las pruebas 360 grados

var Pruebas360 = {
  draw: function(listOfValues){
    var w = 500,
    h = 500;
    
    var colorscale = d3.scale.category10();
    
    //Legend titles
    var LegendOptions = ['Calificación'];
    
    var data = listOfValues;
    //var labels = listOfLabels;
    var dataLength = data.length;
    
    
    var results = [];
    
    if (dataLength > 2) {
        var lista = data.split(",");
        var listaLength = lista.length;
        
        for (var i = 0; i < listaLength; i++) {
            var dat = lista[i].substring(7,11);
            var obj = {axis: i+1, value: dat};
            results.push(obj);
        }    
    } else {
        for (var i = 0; i < 10; i++) {
            var obj = {axis: i+1, value: 0};
            results.push(obj);
        }
    }
    
    //Data
    var d = [ results ];
    //Options for the Radar chart, other than default
    var mycfg = {
      w: w,
      h: h,
      maxValue: 0.6,
      levels: 6,
      ExtraWidthX: 300
    }
    
    //Call function to draw the Radar chart
    //Will expect that data is in %'s
    RadarChart.draw("#chart", d, mycfg);
    
    ////////////////////////////////////////////
    /////////// Initiate legend ////////////////
    ////////////////////////////////////////////
    
    var svg = d3.select('#body')
        .selectAll('svg')
        .append('svg')
        .attr("width", w+300)
        .attr("height", h)
    
    //Create the title for the legend
    var text = svg.append("text")
        .attr("class", "title")
        .attr('transform', 'translate(90,0)') 
        .attr("x", w - 70)
        .attr("y", 10)
        .attr("font-size", "12px")
        .attr("fill", "#404040")
        .text("Resultados 360 grados Radar");
            
    //Initiate Legend	
    var legend = svg.append("g")
        .attr("class", "legend")
        .attr("height", 100)
        .attr("width", 200)
        .attr('transform', 'translate(90,20)') 
        ;
        //Create colour squares
        legend.selectAll('rect')
          .data(LegendOptions)
          .enter()
          .append("rect")
          .attr("x", w - 65)
          .attr("y", function(d, i){ return i * 20;})
          .attr("width", 10)
          .attr("height", 10)
          .style("fill", function(d, i){ return colorscale(i);})
          ;
        //Create text next to squares
        legend.selectAll('text')
          .data(LegendOptions)
          .enter()
          .append("text")
          .attr("x", w - 52)
          .attr("y", function(d, i){ return i * 20 + 9;})
          .attr("font-size", "11px")
          .attr("fill", "#737373")
          .text(function(d) { return d; })
          ;
  }
}

var graphPruebas360 = {
  draw: function(listOfValues){
    var w = 500,
    h = 500;
    
    var colorscale = d3.scale.category10();
    
    //Legend titles
    var LegendOptions = ['Calificación'];
    
    var data = listOfValues;
    var dataLength = data.length;
    
    var labels = ["Responsable","Disponible","Escucha Activa","Cordial/Educado","Interacción con alumnos",
                  "Dominio del tema","Gesticulación de voz","Objetividad","Resolución de dudas","Entrega de notas"];
    var results = [];
    
    if (dataLength > 2) {
        var lista = data.split(",");
        var listaLength = lista.length;
        var labelsLength = lista.length;
        
        if (listaLength > labelsLength) {
          for (var i = 0; i < labelsLength; i++) {
            var dat = lista[i].substring(7,11);
            var obj = {axis: labels[i], value: dat};
            results.push(obj);
          }
        } else {
          for (var i = 0; i < listaLength; i++) {
            var dat = lista[i].substring(7,11);
            var obj = {axis: labels[i], value: dat};
            results.push(obj);
          }
        }
            
        
    } else {
        for (var i = 0; i < 10; i++) {
            var obj = {axis: labels[i], value: 0};
            results.push(obj);
        }
    }
    
    //Data
    var d = [ results ];
    //Options for the Radar chart, other than default
    var mycfg = {
      w: w,
      h: h,
      maxValue: 0.6,
      levels: 6,
      ExtraWidthX: 300
    }
    
    //Call function to draw the Radar chart
    //Will expect that data is in %'s
    RadarChart.draw("#chart", d, mycfg);
    
    ////////////////////////////////////////////
    /////////// Initiate legend ////////////////
    ////////////////////////////////////////////
    
    var svg = d3.select('#body')
        .selectAll('svg')
        .append('svg')
        .attr("width", w+300)
        .attr("height", h)
    
    //Create the title for the legend
    var text = svg.append("text")
        .attr("class", "title")
        .attr('transform', 'translate(90,0)') 
        .attr("x", w - 70)
        .attr("y", 10)
        .attr("font-size", "12px")
        .attr("fill", "#404040")
        .text("Resultados 360 grados Radar");
            
    //Initiate Legend	
    var legend = svg.append("g")
        .attr("class", "legend")
        .attr("height", 100)
        .attr("width", 200)
        .attr('transform', 'translate(90,20)') 
        ;
        //Create colour squares
        legend.selectAll('rect')
          .data(LegendOptions)
          .enter()
          .append("rect")
          .attr("x", w - 65)
          .attr("y", function(d, i){ return i * 20;})
          .attr("width", 10)
          .attr("height", 10)
          .style("fill", function(d, i){ return colorscale(i);})
          ;
        //Create text next to squares
        legend.selectAll('text')
          .data(LegendOptions)
          .enter()
          .append("text")
          .attr("x", w - 52)
          .attr("y", function(d, i){ return i * 20 + 9;})
          .attr("font-size", "11px")
          .attr("fill", "#737373")
          .text(function(d) { return d; })
          ;
  }
}