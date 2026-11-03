const fs=require('fs');const path=require('path');const vm=require('vm');const assert=require('assert');
const context={console,structuredClone,Date,Intl,localStorage:{getItem:()=>null,setItem:()=>{}},window:{}};vm.createContext(context);
const base=path.join(__dirname,'../assets/js');
for(const file of ['data.js','storage.js'])vm.runInContext(fs.readFileSync(path.join(base,file),'utf8'),context);
const checks=[
 ['seed minimums',`startDeployments.length>=3&&startIncidents.length>=6&&startRequests.length>=4&&startReleases.length>=2`],
 ['SLA sample percent',`getSlaPercent(startIncidents)===67`],
 ['SLA critical in 3h',`getSlaState({priority:'critical',status:'new',createdAt:'2026-11-03T00:00:00Z'},settings,Date.parse('2026-11-03T03:00:00Z'))==='on_track'`],
 ['SLA critical breached in 5h',`getSlaState({priority:'critical',status:'new',createdAt:'2026-11-03T00:00:00Z'},settings,Date.parse('2026-11-03T05:00:00Z'))==='breached'`],
 ['SLA resolved on time',`getSlaState({priority:'critical',status:'resolved',createdAt:'2026-11-03T00:00:00Z',resolvedAt:'2026-11-03T02:00:00Z'})==='met'`],
 ['SLA resolved late',`getSlaState({priority:'critical',status:'resolved',createdAt:'2026-11-03T00:00:00Z',resolvedAt:'2026-11-03T05:00:00Z'})==='breached'`],
 ['SemVer patch',`getNextVersion('v1.2.3','patch')==='v1.2.4'`],
 ['SemVer minor',`getNextVersion('v1.2.3','minor')==='v1.3.0'`],
 ['SemVer major',`getNextVersion('v1.2.3','major')==='v2.0.0'`],
 ['HTML escaping',`escapeHTML('<img src="x">').includes('&lt;img')`],
 ['Invalid JSON fallback',`loadData('incidents',startIncidents).length===6`]
];
let failures=0;for(const [name,expression] of checks){try{assert(vm.runInContext(expression,context),name);console.log('PASS',name);}catch(e){console.error('FAIL',name,e.message);failures++;}}process.exitCode=failures?1:0;
