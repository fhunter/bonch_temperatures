<html>
<head>
<meta http-equiv="refresh" content="30">
</head>
<body>
<h1>Список компьютеров</h1>
% for image in names:
<h2>Компьютер {{image}}</h2>
<img src="{{basename}}/graph/{{image}}"><br/>
% end
</body>
</html>
