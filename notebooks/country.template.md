## {{country.name}} Covid-19 status comparison 
{% if country.most_impacted %}
{{country.name}} covid-19 deaths are currently doubling each {{country.growth_rate}} days (observed initial average doubling time is 2.2 days across countries).
{% else %}
{{country.name}}
{% endif %}


Be careful, all those charts use a **logarithmic scale**, because it's the best way to analyze how the epidemic is evolving.
 
The **horizontal position** of the different countries is **adjusted** to have the same fix number of deaths at the position in the graph, **for comparison purposes**.

The vertical position of the different curves is of course impacted too.

"Cases" charts are even more affected too because they use the same time offset that is used for "deaths".

**The most important thing to look at in those charts is the slope of the curve** : the steeper the curve, the shorter the "cases" and "deaths" doubling time.

Feel free to use these charts to raise awareness about the danger Covid-19 represents. 


{% for data_type, chart_infos in country.chart_sections.items() %} 
### {{data_type.capitalize()}} over time
{% for ci in chart_infos %} 
#### {{ci.data_type_string.capitalize()}} ({{ci.chart_type}})
![{{country.name}} covid-19 {{ci.data_type_string}} {{ci.chart_type}} chart]({{url_prefix}}_{{ci.data_type}}.{{ci.chart_suffix}} "{{country.name}} covid-19 {{ci.data_type}} {{ci.chart_type}} chart")   
{% endfor %}
{% endfor %}
