<html>
<head>
</head>
<body>
<h1>Список компьютеров</h1>
<hr/>
<div style="width:100%;height:auto; float:left; text-align:justify;">
<div align=left style="float:left;width=40%;display:inline-block;">
<a href={{basename}}/{{grouped}}/d/>День</a> | <a href={{basename}}/{{grouped}}/w/>Неделя</a> | <a href={{basename}}/{{grouped}}/m/>Месяц</a> | <a href={{basename}}/{{grouped}}/y/>Год</a>
</div>
<div align=right style="float:right;width=40%;display:inline-block;">
<a href={{basename}}/i/{{period}}/>Индивидуально</a> | <a href={{basename}}/g/{{period}}/>Группой</a>
</div>
</div>
<br/>
<hr/>
% for image in names:
<h2>Компьютер {{image}}</h2>
<img src="{{basename}}/graph/{{grouped}}/{{period}}/{{image}}"><br/>
% end
</body>
</html>
