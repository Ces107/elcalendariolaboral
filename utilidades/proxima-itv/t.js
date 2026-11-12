H.run(function(t,e,g){var C=["enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre"],n=g.d.rules[t.tipo];function s(a,u){var T=a.getUTCFullYear(),d=a.getUTCMonth()+u,I=T+Math.floor(d/12),V=(d%12+12)%12;return new Date(Date.UTC(I,V,Math.min(a.getUTCDate(),e.monthDays(I,V+1))))}function D(a){return a.getUTCDate()+" de "+C[a.getUTCMonth()]+" de "+a.getUTCFullYear()}function E(a){var u=a.getUTCFullYear()-t.matr.getUTCFullYear();return s(t.matr,12*u)>a&&u--,u}function f(a){var u=E(a),T=n[2][0][1];return n[2].forEach(function(d){u>=d[0]&&(T=d[1])}),T}function A(a){return a===24?"bienal":a===12?"anual":a===6?"semestral":"cada "+a+" meses"}if(!n)return{err:"Elige el tipo de veh\xEDculo."};if(!t.matr)return{err:"Escribe la fecha de primera matriculaci\xF3n."};if(t.ult&&t.ult<t.matr)return{err:"La \xFAltima ITV no puede ser anterior a la matriculaci\xF3n."};var h=n[1]?s(t.matr,12*n[1]):s(t.matr,n[2][0][1]),r=[],c=t.ult?s(t.ult,f(t.ult)):h;t.ult&&t.ult<h&&n[1]&&(c=h);for(var l=0;l<40&&r.length<8;l++)r.push(c),c=s(c,f(c));var m=e.today?e.today():null,i=r[0];if(m){for(l=0;l<r.length;l++)if(r[l]>=m){i=r[l];break}}var o=m?e.diff(m,i):null,b=r.slice(Math.max(0,r.indexOf(i)),Math.max(0,r.indexOf(i))+6),N='<table class="tbl"><thead><tr><th>ITV</th><th>Antig\xFCedad</th><th>Siguiente</th></tr></thead><tbody>'+b.map(function(a){return"<tr><td>"+D(a)+'</td><td class="num">'+E(a)+" a\xF1os</td><td>"+A(f(a))+"</td></tr>"}).join("")+"</tbody></table>",R=b.map(function(a){return`BEGIN:VEVENT\r
UID:itv-`+e.icsDate(a)+`@elcalendariolaboral.es\r
DTSTAMP:20261112T000000Z\r
DTSTART;VALUE=DATE:`+e.icsDate(a)+`\r
DTEND;VALUE=DATE:`+e.icsDate(e.add(a,1))+`\r
SUMMARY:`+e.icsEsc("Caduca la ITV")+`\r
BEGIN:VALARM\r
ACTION:DISPLAY\r
DESCRIPTION:`+e.icsEsc("Pide cita para la ITV")+`\r
TRIGGER:-P30D\r
END:VALARM\r
END:VEVENT`});return{label:t.ult?"Pr\xF3xima ITV":"ITV",big:D(i),sub:(o===null?"":o<0?"Caducada hace "+-o+" d\xEDas \xB7 ":o===0?"Hoy \xB7 ":"Dentro de "+o+" "+e.plural(o,"d\xEDa","d\xEDas")+" \xB7 ")+E(i)+" a\xF1os \xB7 despu\xE9s, "+A(f(i)),html:N,note:t.ult?"":"Sin \xAB\xDAltima ITV\xBB, las fechas se cuentan desde la matriculaci\xF3n: si alguna vez la pasaste tarde, escribe la fecha real.",ics:{name:"itv.ics",text:`BEGIN:VCALENDAR\r
VERSION:2.0\r
PRODID:-//elcalendariolaboral.es//ITV//ES\r
CALSCALE:GREGORIAN\r
`+R.join(`\r
`)+`\r
END:VCALENDAR\r
`},n:{list:r.slice(0,6).map(e.iso)}}});
