##  COVID-19 {{ date }} report
Feel free to use these charts to raise awareness about the danger Covid-19 represents. 


![Covid-19 Chart for {{main_chart_countries_data.main}}]({{url_prefix}}_main_comparison_day_deaths.png "Covid-19 Cumulated Chart for {{main_chart_countries_data.main}}")

![Covid-19 Chart for {{main_chart_countries_data.scandinavia}}]({{url_prefix}}_scandinavia_comparison_day_deaths.png "Covid-19 Daily Chart for {{main_chart_countries_data.scandinavia}}")

### Most Affected Countries as of {{date}}
{% for country in most_impacted_countries_data %}
[{{country.name }}](countries/{{country.path}})
{% endfor %}

### Other Affected Countries
{% for country in other_countries_data %}
[{{country.name }}](countries/{{country.path}})
{% endfor %}