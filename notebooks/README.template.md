##  COVID-19 {{ date }} report
Feel free to use these charts to raise awareness about the danger Covid-19 represents. 

### Spread comparison 
![Covid-19 Chart for {{main_chart_countries}}]({{url_prefix}}_main_comparison.png "Covid-19 Chart for {{main_chart_countries}}")

### By Country
{% for country in countries %}
[{{country.name }}]({{country.path}})
{% endfor %}