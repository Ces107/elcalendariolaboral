H.run(function(g,a,f){var e={lang:"en",mon:["January","February","March","April","May","June","July","August","September","October","November","December"],wd:["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],de:" ",label:"Due date",between:"Normal window: ",and:" to ",avg:"Average gestation",range:"Usual range",days:" days",from:"Mating",prep:"Get the birthing area ready",today:"Today",dayn:"day ",left:"",togo:" to go",past:"past the due date",late:"past the usual range: call your vet",err:"Enter the mating date.",note:"Averages from veterinary references: every animal, breed and litter varies. Not a substitute for a vet check.",ics:"due-date.ics",sum:"Due date",win:"Birth window"},y={perra:[63,58,72,"Perra","Dog"],gata:[65,58,70,"Gata","Cat"],coneja:[31,28,35,"Coneja","Rabbit"],cerda:[114,111,117,"Cerda","Sow (pig)"],oveja:[147,143,152,"Oveja","Ewe (sheep)"],cabra:[150,145,155,"Cabra","Goat"],vaca:[283,279,292,"Vaca","Cow"],yegua:[340,320,370,"Yegua","Mare (horse)"],burra:[365,335,440,"Burra","Jenny (donkey)"]},n=y[g.especie]||y.perra,o=g.fecha;if(!o)return{err:e.err};function s(r){return e.wd[a.wd(r)]+" "+(e.lang==="en"?r.getUTCDate()+" "+e.mon[r.getUTCMonth()]+" "+r.getUTCFullYear():r.getUTCDate()+e.de+e.mon[r.getUTCMonth()]+e.de+r.getUTCFullYear())}function c(r){return e.lang==="en"?r.getUTCDate()+" "+e.mon[r.getUTCMonth()].slice(0,3):r.getUTCDate()+"/"+(r.getUTCMonth()+1)+"/"+r.getUTCFullYear()}var d=a.add(o,n[0]),i=a.add(o,n[1]),l=a.add(o,n[2]),E=a.add(i,-7),T=[[e.from,s(o)],[e.avg,n[0]+e.days],[e.range,n[1]+"\u2013"+n[2]+e.days],[e.prep,s(E),"sub"],[e.label,s(d),"tot"]],b=a.today?a.today():null,t=null;b&&(t=a.diff(o,b),t>=0&&t<=n[2]+30&&T.push([e.today,t>n[2]?e.late:t>n[0]?e.dayn+t+" \xB7 "+e.past:e.dayn+t+" \xB7 "+e.left+(n[0]-t)+e.days+(e.togo||"")]));function D(r,C,h,v){return`BEGIN:VEVENT\r
UID:`+v+a.icsDate(o)+`@elcalendariolaboral.es\r
DTSTAMP:20261112T000000Z\r
DTSTART;VALUE=DATE:`+a.icsDate(r)+`\r
DTEND;VALUE=DATE:`+a.icsDate(a.add(C,1))+`\r
SUMMARY:`+a.icsEsc(h)+`\r
TRANSP:TRANSPARENT\r
END:VEVENT\r
`}var u=e.lang==="en"?n[4]:n[3],A=`BEGIN:VCALENDAR\r
VERSION:2.0\r
PRODID:-//elcalendariolaboral.es//gestacion//`+(e.lang==="en"?"EN":"ES")+`\r
CALSCALE:GREGORIAN\r
`+D(d,d,e.sum+" \xB7 "+u,"g")+D(i,l,e.win+" \xB7 "+u,"w")+`END:VCALENDAR\r
`;return{label:e.label+" \xB7 "+u,big:s(d),sub:e.between+c(i)+e.and+c(l),rows:T,note:e.note,ics:{name:e.ics,text:A},n:{due:a.iso(d),lo:a.iso(i),hi:a.iso(l),days:n[0]}}});
