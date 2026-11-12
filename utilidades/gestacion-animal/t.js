H.run(function(c,e,f){var a={mon:["enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre"],wd:["lunes","martes","mi\xE9rcoles","jueves","viernes","s\xE1bado","domingo"],de:" de ",label:"Parto previsto",between:"Lo normal: entre el ",and:" y el ",avg:"Gestaci\xF3n media",range:"Rango habitual",days:" d\xEDas",from:"Cubrici\xF3n",prep:"Preparar la zona de parto",today:"Hoy",dayn:"d\xEDa ",left:"faltan ",past:"ya pas\xF3 la fecha prevista",late:"pasado el rango habitual: consulta al veterinario",err:"Pon la fecha de la cubrici\xF3n.",note:"Promedios de manuales veterinarios: cada animal, raza y camada var\xEDa. No sustituye la revisi\xF3n veterinaria.",ics:"parto-previsto.ics",sum:"Parto previsto",win:"Ventana de parto",num_sep:","},g={perra:[63,58,72,"Perra","Dog"],gata:[65,58,70,"Gata","Cat"],coneja:[31,28,35,"Coneja","Rabbit"],cerda:[114,111,117,"Cerda","Sow (pig)"],oveja:[147,143,152,"Oveja","Ewe (sheep)"],cabra:[150,145,155,"Cabra","Goat"],vaca:[283,279,292,"Vaca","Cow"],yegua:[340,320,370,"Yegua","Mare (horse)"],burra:[365,335,440,"Burra","Jenny (donkey)"]},n=g[c.especie]||g.perra,t=c.fecha;if(!t)return{err:a.err};function s(r){return a.wd[e.wd(r)]+" "+(a.lang==="en"?r.getUTCDate()+" "+a.mon[r.getUTCMonth()]+" "+r.getUTCFullYear():r.getUTCDate()+a.de+a.mon[r.getUTCMonth()]+a.de+r.getUTCFullYear())}function b(r){return a.lang==="en"?r.getUTCDate()+" "+a.mon[r.getUTCMonth()].slice(0,3):r.getUTCDate()+"/"+(r.getUTCMonth()+1)+"/"+r.getUTCFullYear()}var i=e.add(t,n[0]),l=e.add(t,n[1]),d=e.add(t,n[2]),v=e.add(l,-7),p=[[a.from,s(t)],[a.avg,n[0]+a.days],[a.range,n[1]+"\u2013"+n[2]+a.days],[a.prep,s(v),"sub"],[a.label,s(i),"tot"]],m=e.today?e.today():null,o=null;m&&(o=e.diff(t,m),o>=0&&o<=n[2]+30&&p.push([a.today,o>n[2]?a.late:o>n[0]?a.dayn+o+" \xB7 "+a.past:a.dayn+o+" \xB7 "+a.left+(n[0]-o)+a.days+(a.togo||"")]));function T(r,C,y,D){return`BEGIN:VEVENT\r
UID:`+D+e.icsDate(t)+`@elcalendariolaboral.es\r
DTSTAMP:20261112T000000Z\r
DTSTART;VALUE=DATE:`+e.icsDate(r)+`\r
DTEND;VALUE=DATE:`+e.icsDate(e.add(C,1))+`\r
SUMMARY:`+e.icsEsc(y)+`\r
TRANSP:TRANSPARENT\r
END:VEVENT\r
`}var u=a.lang==="en"?n[4]:n[3],E=`BEGIN:VCALENDAR\r
VERSION:2.0\r
PRODID:-//elcalendariolaboral.es//gestacion//`+(a.lang==="en"?"EN":"ES")+`\r
CALSCALE:GREGORIAN\r
`+T(i,i,a.sum+" \xB7 "+u,"g")+T(l,d,a.win+" \xB7 "+u,"w")+`END:VCALENDAR\r
`;return{label:a.label+" \xB7 "+u,big:s(i),sub:a.between+b(l)+a.and+b(d),rows:p,note:a.note,ics:{name:a.ics,text:E},n:{due:e.iso(i),lo:e.iso(l),hi:e.iso(d),days:n[0]}}});
