## {{country.name}} Covid-19 status comparison 
{% if country.most_impacted %}
{{country.name}} covid-19 deaths are currently doubling each {{country.growth_rate}} days (observed average doubling time is 2.2 days across countries).
{% else %}
{{country.name}}
{% endif %}


Be careful, all those charts use a logarithmic scale, because it's the best way to analyze how the epidemic is evolving.
 
The horizontal position of the different countries is adjusted to have the same fix number of deaths at the position in the graph, for comparison purpose.

The vertical position of the different curves is of course impacted too.

"Cases" charts are even more affected too because they use the same time offset that is used for "deaths".

The only important thing to look at in those charts is the slope of the curve : the steeper the curve, the shorter the "cases" and "deaths" doubling time.



{% for data_type, chart_infos in country.chart_sections.items() %} 
### {{data_type.capitalize()}} over time
{% for ci in chart_infos %} 
#### {{ci.chart_type.capitalize()}}
![{{country.name}} covid-19 {{ci.data_type}} {{ci.chart_type}} chart]({{url_prefix}}_deaths.{{ci.chart_suffix}} "{{country.name}} covid-19 {{ci.data_type}} {{ci.chart_type}} chart")   
{% endfor %}
{% endfor %}
