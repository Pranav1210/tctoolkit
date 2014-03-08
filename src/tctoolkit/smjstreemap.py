'''
Display the Source Monitor data as 'treemap' using d3js javascript library.
This will generate an HTML file as output.

Copyright (C) 2014 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit) and is released under the
New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at http://code.google.com/p/tctoolkit/
'''

import sys, os, string
import json
from optparse import OptionParser

from thirdparty.templet import *
from sourcemon import *

@stringfunction
def TreemapHtml(treemap):
    '''<!DOCTYPE html>
    <html>
      <head>
        <meta http-equiv="content-type" content="text/html;charset=utf-8">
        <title>d3.js ~ Treemap</title>
        <script type="text/javascript" src="./thirdparty/javascript/d3js/d3.js"></script>
        <style type="text/css">
                body {
              font: 14px Helvetica Neue;
              text-rendering: optimizeLegibility;
              margin-top: 1em;
              overflow-y: scroll;
            }
            
            .body {
              width: 960px;
              margin: auto;
            }
             
            h1 {
              font-size: 36px;
              font-weight: 300;
              margin-bottom: .3em;
            }
            
            .highlight {
              font: 12px monospace;
            }
                        
            .cell {
                border: 1px solid #FFFFFF;
                font: 10px/12px sans-serif;
                overflow: hidden;
                position: absolute;
                text-indent: 2px;
            }
        </style>
      </head>
      <body>
        <div class="body">
            <div class="content">
                <h1 id='treemap'>Source Monitor Treemap</h1>
                <div>
                    <div style="display:inline-block">
                        <select class="properties" id="size">
                        </select>
                    </div>
                    <div style="display:inline-block">
                        <select class="properties" id="color">
                        </select>
                    </div>
                </div>
                <div class='gallery' id='chart'></div>
            </div>
        </div>
        
        <script>
        // data
        var treemapData = ${treemap.getJson()};
        var proplist = ${treemap.getPropertyNames()};
        </script>
        <script>
        var w = 960,
        h = 500;
        
        var colorMap = d3.scale.linear()
            .domain([-1, 0, 1])
            .range(["green", "white", "red"]);
        
        function updateColorMap(){
            var propdata = d3.select(getCurPropElem("#color")).datum();
            colorMap = d3.scale.linear()
                .domain([propdata.min, propdata.threshold, propdata.max])
                .range(["green", "white", "red"]);
        }
        
        function getCurPropElem(sel) {
            // get the current property name from the dropdown 'sel'.
            var elem = d3.select(sel)[0][0];
            var propname = elem[elem.selectedIndex];
            return propname;
        }
    
        function valueFunc(d) {
            var valueprop = getCurPropElem("#size").text;
            return d[valueprop]; 
        }
        
        function colorFunc(d) {
            var colorprop = getCurPropElem("#color").text;
            return d[colorprop]; 
        }
        
        var treemap = d3.layout.treemap()
            .size([w, h])
            .sticky(true)
            .value(valueFunc);
        
        var div = d3.select("#chart").append("div")
            .style("position", "relative")
            .style("width", w + "px")
            .style("height", h + "px");
    
        function redrawTreemap() {
            // set colors domain range before drawing the treemap
            updateColorMap();
            
            div.selectAll("div")
                .data(treemap.value(valueFunc))
              .transition()
                .duration(1500)
                .style("background", function(d) { return d.children ? null : colorMap(colorFunc(d)); })
                .call(cell);
        }
        function drawTreemap(json) {
          // set colors domain range before drawing the treemap
          updateColorMap();
          
          div.data([json]).selectAll("div")
              .data(treemap.nodes)
            .enter().append("div")
              .attr("class", "cell")
              .style("background", function(d) { return d.children ? null : colorMap(colorFunc(d)); })
              .call(cell)
              .text(function(d) { return d.children ? null : d.name; });
        
            
          d3.select("#size").on("change", redrawTreemap);
          d3.select("#color").on("change", redrawTreemap);
        };
        
        function cell() {
          this
              .style("left", function(d) { return d.x + "px"; })
              .style("top", function(d) { return d.y + "px"; })
              .style("width", function(d) { return d.dx - 1 + "px"; })
              .style("height", function(d) { return d.dy - 1 + "px"; });
        }
        
        function updatePropertyDropdown(sel, proplist) {
            //update the list of properties for color and size dropdown
            d3.selectAll(sel).selectAll().data(proplist)
                .enter().append("option")
                    .attr("value", function(d) { return d.name;})
                    .text(function(d) { return d.name});
            d3.select("#size option[value='Lines']").attr("selected", "selected");
            d3.select("#color option[value='MaxComplexity']").attr("selected", "selected");
        }
        
        updatePropertyDropdown(".properties", proplist);
        drawTreemap(treemapData);
    
        </script>
      </body>
    </html>
    '''
 
class D3JSTreemap(SMTree):
    '''
    Class to represent the d3js treemap code generator.
    1. it will copy the d3js file.
    2. Generate the neccessary javascript JSON/Data code
    3. Generate the html template
    '''
    def __init__(self, smfile):
        super(D3JSTreemap, self).__init__(smfile)
        self.propnames = dict()
        
    def getNodeDict(self, node):
        '''
        get node dictionary for node. python 'json' module will encode this dictionary in json
        '''
        
        nodedict = dict()
        nodedict['name'] = node.name
        for prop, value in node.properties.iteritems():
            nodedict[prop] = value
            minmax = self.propnames.get(prop,(sys.maxint,0))
            minmax = (min(minmax[0], value), max(minmax[1], value))
            self.propnames[prop] = minmax
        
        children = list()
        for childname, childnode in node.children.iteritems():
            children.append(self.getNodeDict(childnode))
        nodedict['children'] = children
        return nodedict
    
    def getJson(self):
        '''
        convert the treemap data to json data as required by d3js treemap
        '''
        return json.dumps(self.getNodeDict(self))
    
    def getPropertyNames(self):
        proplist = list()
        for prop, minmax in self.propnames.iteritems():
            propdict = {"name":prop, "min":minmax[0], "max":minmax[1], "threshold":COLOR_PROP_CONFIG.get(prop,minmax[0])}
            proplist.append(propdict)
        
        return json.dumps(proplist)
    
    
def RunMain():
    usage = "usage: %prog [options] <source monitor xml or csv filename> <treemap html name>"
    description = '''SourceMonitor treemap display using d3js visualization library.
    (C) Nitin Bhide nitinbhide@thinkingcraftsman.in
    '''
    
    parser = OptionParser(usage)

    (options, args) = parser.parse_args()
    
    if( len(args) < 1):
        print "Invalid number of arguments. Use smtreemapjs.py --help to see the details."
    else:            
        smfile = args[0]
        htmlfilename = args[1]
        treemap = D3JSTreemap(smfile)
        with open(htmlfilename, "w") as outf:
            outf.write(TreemapHtml(treemap))
            
if( __name__ == "__main__"):
    RunMain()