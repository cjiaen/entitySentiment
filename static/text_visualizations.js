//load in json data file
/*
d3.json('/static/test_output.json', function(data){
    console.log(data);
});
*/
$.getJSON('/static/test_output.json', function(data){
    var nodes_dict = {};
    var links = [];
    var width = 960, height = 500;

    // Compute the distinct nodes from the links.
    data['relationship'].forEach(function(link) {
        //link.subject = nodes[link.subject] || (nodes[link.subject] = {name: link.subject});
        //link.object = nodes[link.object] || (nodes[link.object] = {name: link.object});
        nodes_dict[link.subject] = {name: link.subject};
        nodes_dict[link.object] = {name: link.object};
        var score = link.sentiment;
        var type = "neutral";
        
        if(score < -0.2){
            type = 'negative'
        } else if(score > 0.2){
            type = 'positive'
        };
        
        links.push({'source':link.subject, 'target':link.object, 'score':score, 'type':type});
    });

    var nodes = Object.values(nodes_dict);

    console.log(nodes);
    console.log(links);

    //set up the simulation 
    var simulation = d3.forceSimulation()
        .nodes(nodes);

    var link_force =  d3.forceLink(links)
                        .id(function(d) { return d.name; });
    simulation
        .force("charge_force", d3.forceManyBody().strength(-30))
        .force("center_force", d3.forceCenter(width / 2, height / 2))
        .force("links",link_force);

    //add tick instructions: 
    simulation.on("tick", tickActions);

    //set up svg canvas
    var svg = d3.select("body").append("svg")
        .attr("width", width)
        .attr("height", height);
   
    var arcs = svg.append('g')
                    .selectAll('path')
                    .data(links)
                    .enter()
                    .append("path")
                    .attr("class", "links")
                    .attr("marker-end", function(d) { return "url(#" + d.index + ")"; })
                    .style('stroke', function(d){
                        if(d.type == 'positive'){return "blue";}
                        else if (d.type == 'negative'){return "red";}
                        else {return "black";}
                    })
                    .attr('stroke-width', function(d) {return Math.abs(parseFloat(d.score)*10);});
    
    var circle = svg.append('g')
                    .attr("class", "nodes")
                    .selectAll('circle')
                    .data(nodes)
                    .enter()
                    .append('circle')
                    .attr('r', 5)
                    .attr("fill", "grey");

    svg.append("defs")
        .selectAll("marker")
        .data(links)
        .enter()
        .append("marker")
        .attr("id", function(d) { return d.index; })
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 15)
        .attr("refY", -1.5)
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
        .append("path")
        .attr("d", "M0,-5L10,0L0,5")
        .style('fill', function(d){
            if(d.type == 'positive'){return "blue";}
            else if (d.type == 'negative'){return "red";}
            else {return "black";}
        });

    var text = svg.append('g')
                    .attr('class', "text_label")
                    .selectAll('text')
                    .data(nodes)
                    .enter()
                    .append('text')
                    .attr('x', 10)
                    .attr('y', 5)
                    .text(function(d){return d.name;});
    
    var drag_handler = d3.drag()
                        .on("start", drag_start)
                        .on("drag", drag_drag)
                        .on("end", drag_end);

    drag_handler(circle);

    function drag_start(d) {
        if (!d3.event.active) simulation.alphaTarget(0.3).restart();
           d.fx = d.x;
           d.fy = d.y;
    }
       
    function drag_drag(d) {
         d.fx = d3.event.x;
         d.fy = d3.event.y;
    }
       
    function drag_end(d) {
        if (!d3.event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }

    function linkArc(d) {
        var dx = d.target.x - d.source.x,
            dy = d.target.y - d.source.y,
            dr = Math.sqrt(dx * dx + dy * dy);
        return "M" + d.source.x + "," + d.source.y + "A" + dr + "," + dr + " 0 0,1 " + d.target.x + "," + d.target.y;
    } 

    function tickActions() {
        //update circle positions each tick of the simulation 
        circle
            .attr('transform', transform);
            
        arcs
            .attr('d', linkArc);
        
        text
            .attr('transform', transform);
    }

    function transform(d) {
        return "translate(" + d.x + "," + d.y + ")";
    }
});

/*
//create force diagram
    var force = d3.layout.force()
        .nodes(d3.values(nodes))
        .links(links)
        .size([width, height])
        .start();
        //.linkDistance(60)
        //.charge(-300)
        //.on("tick", tick);


    
    // Per-type markers, as they don't inherit styles.

    svg.append("defs").selectAll("marker")
        .data(["suit", "licensing", "resolved"])
        .enter().append("marker")
        .attr("id", function(d) { return d; })
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 15)
        .attr("refY", -1.5)
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
        .append("path")
        .attr("d", "M0,-5L10,0L0,5");

   var path = svg.append("g").selectAll("path")
   .data(force.links())
   .enter().append("path")
   .attr("class", function(d) { return "link " + d.type; })
   .attr("marker-end", function(d) { return "url(#" + d.type + ")"; });

var circle = svg.append("g").selectAll("circle")
   .data(force.nodes())
   .enter().append("circle")
   .attr("r", 15)
   .call(force.drag);

var text = svg.append("g").selectAll("text")
   .data(force.nodes())
   .enter().append("text")
   .attr("x", 8)
   .attr("y", ".31em")
   .text(function(d) { return d.name; });

// Use elliptical arc path segments to doubly-encode directionality.
function tick() {
 path.attr("d", linkArc);
 circle.attr("transform", transform);
 text.attr("transform", transform);
}

function linkArc(d) {
 var dx = d.target.x - d.source.x,
     dy = d.target.y - d.source.y,
     dr = Math.sqrt(dx * dx + dy * dy);
 return "M" + d.source.x + "," + d.source.y + "A" + dr + "," + dr + " 0 0,1 " + d.target.x + "," + d.target.y;
}

function transform(d) {
 return "translate(" + d.x + "," + d.y + ")";
}
*/


