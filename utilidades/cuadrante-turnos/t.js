H.run(function(t,r,G){var D={M:"Ma\xF1ana",T:"Tarde",N:"Noche",D:"D\xEDa 12 h",G:"Guardia 24 h",X:"Trabajo",L:"Libre"},p={M:8,T:8,N:8,D:12,G:24,X:t.hx,L:0},v=["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"],h=String(t.seq).toUpperCase().replace(/[^A-Z]/g,"");if(!/^[MTNDGXL]{1,60}$/.test(h))return{err:"Secuencia: solo M, T, N, D, G, X y L (m\xE1ximo 60)."};if(!t.start)return{err:"Elige el d\xEDa en que empieza el ciclo."};if(!(t.hx>0&&t.hx<=24))return{err:"Horas por turno: de 1 a 24."};for(var M=r.holidayMap(t.lugar),U=Date.UTC(2027,0,1),i={},c=0,b=0,E=0,A=[],N="",T=h.length,n=0;n<12;n++){for(var S=new Date(Date.UTC(2027,n,1)),g=r.monthDays(2027,n+1),R=r.wd(S),o=[],f=0;f<R;f++)o.push('<td class="o"></td>');for(var u=1;u<=g;u++){var s=new Date(Date.UTC(2027,n,u)),C=(r.diff(t.start,s)%T+T)%T,e=h.charAt(C),a=M[r.iso(s)];a&&t.fl&&(e="L"),i[e]=(i[e]||0)+1,e!=="L"&&(b++,c+=p[e],a&&E++,A.push(`BEGIN:VEVENT\r
UID:`+r.icsDate(s)+"-"+e+`@elcalendariolaboral.es\r
DTSTAMP:20261112T000000Z\r
DTSTART;VALUE=DATE:`+r.icsDate(s)+`\r
DTEND;VALUE=DATE:`+r.icsDate(r.add(s,1))+`\r
SUMMARY:`+r.icsEsc(D[e]+(a?" \xB7 "+a[1]:""))+`\r
TRANSP:TRANSPARENT\r
END:VEVENT`)),o.push('<td class="s-'+e+(a?" hol":"")+'"'+(a?' title="'+r.esc(a[1])+'"':"")+">"+u+(e!=="L"?"<b>"+e+"</b>":"")+"</td>")}for(;o.length%7;)o.push('<td class="o"></td>');for(var L="",d=0;d<o.length;d+=7)L+="<tr>"+o.slice(d,d+7).join("")+"</tr>";N+='<div class="cq-m"><table><caption>'+v[n]+"</caption><thead><tr><th>L</th><th>M</th><th>X</th><th>J</th><th>V</th><th>S</th><th>D</th></tr></thead><tbody>"+L+"</tbody></table></div>"}var V=Object.keys(D).filter(function(l){return i[l]}).map(function(l){return'<li><i class="s-'+l+'"></i>'+D[l]+" \xB7 <b>"+i[l]+"</b></li>"}).join("")+'<li><i class="hol" style="box-shadow:inset 0 0 0 2px #c8102e"></i>Festivo</li>',m=`BEGIN:VCALENDAR\r
VERSION:2.0\r
PRODID:-//elcalendariolaboral.es//Cuadrante de turnos 2027//ES\r
CALSCALE:GREGORIAN\r
X-WR-CALNAME:Turnos 2027\r
`+A.join(`\r
`)+(A.length?`\r
`:"")+`END:VCALENDAR\r
`;return{label:"D\xEDas de trabajo en 2027",big:b,sub:r.num(c,0)+" h \xB7 "+(i.L||0)+" libres \xB7 "+E+" festivos trabajados \xB7 "+r.esc(t.lugar_label),html:'<h2 class="cq-h">Cuadrante de turnos 2027 \xB7 '+r.esc(h)+'</h2><ul class="cq-leg">'+V+'</ul><div class="cq-y">'+N+"</div>",print:!0,ics:{name:"turnos-2027.ics",text:m},n:{worked:b,hours:c,cnt:i,holWorked:E}}});
