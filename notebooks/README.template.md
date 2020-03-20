##  COVID-19 {{ date }} report

### Spread comparison 
![Chart for {{main_chart_countries}}](https://raw.githubusercontent.com/madlag/coronavirus_study/master/notebooks/graphs/{{date}}/{{date}}_main_comparison.png "Logo Title Text 1")

{% for country in countries %}
 <li><a href="{{country.name}}">{{country.name }}</a></li>
{% endfor %}