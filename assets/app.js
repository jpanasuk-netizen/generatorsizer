/* GeneratorSizer calculators — vanilla JS, no dependencies.
   Wattage presets use published manufacturer / DOE / consumer-reports ranges, rounded to
   conservative typical values. All estimates rounded UP to be safe. */
"use strict";

var PRESETS = [
  { name:"Refrigerator (Energy Star, 20 cu ft)", run:150,  surge:600 },
  { name:"Chest freezer (10–15 cu ft)",          run:200,  surge:600 },
  { name:"Well pump — 1/2 HP",                   run:1000, surge:2100 },
  { name:"Well pump — 3/4 HP",                   run:1500, surge:3000 },
  { name:"Sump pump — 1/2 HP",                   run:800,  surge:1300 },
  { name:"Window AC — 10,000 BTU",               run:900,  surge:1400 },
  { name:"Central AC — 2.5 ton",                 run:3500, surge:5000 },
  { name:"Furnace fan — 1/3 HP",                 run:700,  surge:1400 },
  { name:"Space heater",                         run:1500, surge:1500 },
  { name:"LED lights (whole home)",              run:80,   surge:80 },
  { name:"Microwave (1,000 W)",                  run:1000, surge:1000 },
  { name:"TV + internet + phones",               run:150,  surge:150 },
  { name:"Washing machine",                      run:1150, surge:2300 },
  { name:"Electric water heater",                run:4500, surge:4500 },
  { name:"Coffee maker",                         run:1000, surge:1000 },
  { name:"Electric skillet / hot plate",         run:1200, surge:1200 }
];
// Appliance items the user has added: {name, run, surge, qty}
var loads = [];

function el(id){ return document.getElementById(id); }
function fmt(n){ return Math.round(n).toLocaleString("en-US"); }
function ceilTo(n, step){ return Math.ceil(n/step)*step; }

/* ---------- Tabs ---------- */
function showTab(key, btn){
  document.querySelectorAll(".panel").forEach(function(p){ p.classList.remove("active"); });
  document.querySelectorAll(".tabs button").forEach(function(b){ b.setAttribute("aria-selected","false"); });
  el(key).classList.add("active");
  if(btn) btn.setAttribute("aria-selected","true");
}

/* ---------- Load builder ---------- */
function presetOptions(){
  var html = '<option value="">— pick an appliance —</option>';
  PRESETS.forEach(function(p,i){
    html += '<option value="'+i+'">'+p.name+" ("+fmt(p.run)+" W)</option>";
  });
  html += '<option value="custom">Custom…</option>';
  return html;
}

function addLoad(name, run, surge){
  loads.push({ name:name||"Custom load", run:run||0, surge:surge||0, qty:1 });
  renderLoads();
}

function renderLoads(){
  var wrap = el("loadRows");
  if(!loads.length){
    wrap.innerHTML = '<p class="small">No loads yet — pick an appliance above, or add a custom row.</p>';
  } else {
    var rows = "";
    loads.forEach(function(l,i){
      rows += '<div class="load-row">'+
        '<input type="text" value="'+l.name.replace(/"/g,"&quot;")+'" data-i="'+i+'" data-f="name" aria-label="Appliance name">'+
        '<input type="number" min="0" value="'+l.run+'" data-i="'+i+'" data-f="run" aria-label="Running watts">'+
        '<input type="number" min="0" value="'+l.surge+'" data-i="'+i+'" data-f="surge" aria-label="Starting watts">'+
        '<input type="number" min="1" value="'+l.qty+'" data-i="'+i+'" data-f="qty" aria-label="Quantity">'+
        '<button class="del" data-del="'+i+'" aria-label="Remove '+l.name+'">✕</button>'+
      '</div>';
    });
    wrap.innerHTML = '<div class="load-row load-head"><span>Appliance</span><span class="num">Run W</span><span class="num">Start W</span><span class="num">Qty</span><span></span></div>'+rows;
  }
  el("genResult").hidden = true;
  el("genResult").innerHTML = "";
}

document.addEventListener("click", function(e){
  var add = e.target.closest("[data-add]");
  if(add){
    var sel = el("presetSelect");
    if(sel.value === "") return;
    if(sel.value === "custom"){ addLoad("Custom load", 0, 0); }
    else { var p = PRESETS[+sel.value]; addLoad(p.name, p.run, p.surge); }
    sel.value = "";
    return;
  }
  var del = e.target.closest("[data-del]");
  if(del){ loads.splice(+del.getAttribute("data-del"),1); renderLoads(); }
});
document.addEventListener("input", function(e){
  var inp = e.target.closest(".load-row input[data-f]");
  if(!inp) return;
  var i = +inp.getAttribute("data-i"), f = inp.getAttribute("data-f");
  loads[i][f] = f === "name" ? inp.value : Math.max(0, +inp.value || 0);
});

/* ---------- 1. Generator sizing ---------- */
// Gas: a typical portable inverter generator burns roughly 1 gal/hr per 7,000 W of
// rated output at 50% load (3,500 W class ≈ 0.5 gal/hr; 7,500 W class ≈ 1.0 gal/hr).
// Propane: ~27% less energy per gallon than gasoline (91,600 vs 125,000 BTU/gal),
// so consumption in gal-propane/hr ≈ gal-gas/hr × 1.37. A 20 lb tank holds 4.7 gal.
function sizeGenerator(){
  if(!loads.length){ alert("Add at least one appliance first."); return; }
  var headroom = 1 + (parseFloat(el("headroom").value) || 20)/100;
  var hrsDay   = Math.max(1, parseFloat(el("hrsDay").value) || 8);
  var tankGal  = Math.max(0.5, parseFloat(el("tankGal").value) || 4);

  var runTotal = 0, maxSurge = 0, surgeItem = "", surgeRun = 0;
  loads.forEach(function(l){
    var r = l.run * l.qty, s = l.surge * l.qty;
    runTotal += r;
    if(s > maxSurge){ maxSurge = s; surgeItem = l.name; surgeRun = r; }
  });
  // Peak demand = all running loads + the extra surge draw of the single biggest starter
  var extraSurge = Math.max(0, maxSurge - surgeRun);
  var peak = runTotal + extraSurge;
  var rec  = ceilTo(peak * headroom, 500);

  var galHr50 = rec / 7000;           // gasoline gal/hr at 50% load
  var runtime = tankGal / galHr50;    // hours at 50% load
  var proGalHr = galHr50 * 1.37;
  var runtimePro = (tankGal / proGalHr);

  var html = '<div class="big">'+fmt(rec)+' <span class="unit">watts recommended</span></div>'+
    '<p class="note">Running load '+fmt(runTotal)+' W · worst startup surge '+fmt(maxSurge)+' W ('+surgeItem+') · peak demand '+fmt(peak)+' W · +'+Math.round((headroom-1)*100)+'% headroom.</p>'+
    '<div class="grid2">'+
      '<div class="stat"><b>'+fmt(peak)+'</b><span>Peak watts you actually draw</span></div>'+
      '<div class="stat"><b>≥ '+fmt(peak)+'</b><span>Surge rating the generator needs</span></div>'+
      '<div class="stat"><b>'+runtime.toFixed(1)+' h</b><span>Gas runtime @50% load ('+tankGal+' gal tank)</span></div>'+
      '<div class="stat"><b>'+(galHr50*hrsDay).toFixed(1)+' gal/day</b><span>Gasoline use at '+hrsDay+' h/day (50% load)</span></div>'+
      '<div class="stat"><b>'+runtimePro.toFixed(1)+' h</b><span>Propane runtime, same tank volume</span></div>'+
      '<div class="stat"><b>'+(proGalHr*hrsDay*4.24).toFixed(1)+' lb/day</b><span>Propane use at '+hrsDay+' h/day (4.24 lb/gal)</span></div>'+
    '</div>'+
    '<p class="note">Propane delivers ~10% less running wattage than gasoline on dual-fuel models, and propane never goes stale in storage. Runtime figures assume a steady 50% load — real use is cyclical, so expect longer.</p>';
  var box = el("genResult"); box.hidden = false; box.innerHTML = html;
}

/* ---------- 2. Inverter sizing ---------- */
function sizeInverter(){
  var cont = Math.max(0, parseFloat(el("invCont").value) || 0);
  if(!cont){ alert("Enter your total continuous AC load in watts."); return; }
  var kind = el("invKind").value;         // resistive | motor | compressor | mixed
  var f = kind === "resistive" ? 1 : kind === "motor" ? 3 : kind === "compressor" ? 4 : 2;
  var surgeNeed = cont * f;
  var contRec = ceilTo(cont * 1.25, 100); // 25% headroom on continuous rating
  var surgeRec = ceilTo(surgeNeed * 1.1, 100);
  var wireLoss = cont / 0.92 / 12;        // approx DC amps drawn at 12V incl. 8% inverter loss
  var box = el("invResult"); box.hidden = false;
  box.innerHTML = '<div class="big">'+fmt(contRec)+' W <span class="unit">continuous · '+fmt(surgeRec)+' W surge</span></div>'+
    '<div class="grid2">'+
      '<div class="stat"><b>'+fmt(cont)+'</b><span>Your continuous load</span></div>'+
      '<div class="stat"><b>'+f+'×</b><span>Surge factor ('+kind+' loads)</span></div>'+
      '<div class="stat"><b>'+wireLoss.toFixed(0)+' A</b><span>DC draw at 12 V (incl. ~8% inverter loss)</span></div>'+
      '<div class="stat"><b>≥ '+fmt(contRec*1.0)+'</b><span>Continuous inverter rating to buy</span></div>'+
    '</div>'+
    '<p class="note">Pure-sine-wave only for electronics, microwaves, and anything with a motor. Modified-sine inverters run hot and can kill compressor motors — the $40 saved is not worth it.</p>';
}

/* ---------- 3. Battery runtime for inverter setups ---------- */
function sizeBatteryRuntime(){
  var ah = Math.max(0, parseFloat(el("btAh").value) || 0);
  var v  = parseFloat(el("btV").value) || 12;
  var w  = Math.max(1, parseFloat(el("btLoad").value) || 0);
  var chem = el("btChem").value;      // lifepo4 0.8 | agm 0.5
  var dod = chem === "lifepo4" ? 0.80 : 0.50;
  if(!ah || !w){ alert("Enter battery Ah and load watts."); return; }
  var usable = ah * v * dod * 0.88;   // 88% average inverter efficiency
  var hrs = usable / w;
  var cycles = chem === "lifepo4" ? "~3,000" : "~500";
  var box = el("btResult"); box.hidden = false;
  box.innerHTML = '<div class="big">'+hrs.toFixed(1)+' <span class="unit">hours of runtime</span></div>'+
    '<div class="grid2">'+
      '<div class="stat"><b>'+fmt(usable)+'</b><span>Usable Wh (after '+Math.round(dod*100)+'% DoD + inverter loss)</span></div>'+
      '<div class="stat"><b>'+fmt(ah*v)+'</b><span>Nameplate Wh stored</span></div>'+
      '<div class="stat"><b>'+fmt(w)+'</b><span>Continuous AC load</span></div>'+
      '<div class="stat"><b>'+cycles+'</b><span>Approx cycles before replacement</span></div>'+
    '</div>'+
    '<p class="note">Batteries deliver less capacity at high draw rates (Peukert effect) — lead-acid especially. If your load is more than C/5 of the bank rating, knock 15% off these hours. Compare fuel costs on the <a href="generator-sizing-calculator.html">generator sizing page</a>.</p>';
}

/* ---------- 4. Transfer switch load planner ---------- */
function planSwitch(){
  var text = el("tsCircuits").value.trim();
  if(!text){ alert("List your backup circuits, one per line."); return; }
  var total = 0, rows = "";
  text.split("\n").forEach(function(line){
    line = line.trim(); if(!line) return;
    var m = line.match(/^(.*?)\s*[-–:]\s*([\d,]+)(?:\s*w(?:att)?s?)?\s*$/i);
    var name = m ? m[1] : line;
    var w = m ? parseFloat(m[2].replace(/,/g,"")) : 0;
    total += w;
    rows += '<tr><td>'+name+'</td><td class="num">'+fmt(w)+'</td></tr>';
  });
  // Standard manual transfer switches: 30 A = 7,200 W, 50 A = 12,000 W @ 240 V (0.8 PF design margin)
  var options = [ [30,7200], [50,12000], [100,24000] ];
  var rec = options.find(function(o){ return o[1] >= total; });
  var box = el("tsResult"); box.hidden = false;
  var recTxt = rec ? rec[0]+' A / '+rec[1]+' W switch' : 'more than 24 kW — talk to an electrician about a whole-house automatic switch';
  box.innerHTML = '<div class="big">'+fmt(total)+' <span class="unit">watts of backup circuits</span></div>'+
    '<table><tr><th>Circuit</th><th class="num">Watts</th></tr>'+rows+'</table>'+
    '<p><strong>Fits a '+recTxt+'</strong> (switch rating ÷ 1.25 safety must cover your total).</p>'+
    '<p class="note">Manual switches are ~$400–700 installed; automatic standby transfer switches add $2,000+. A hardwired transfer switch is required by code — never back-feed a dryer outlet.</p>';
}

/* ---------- init ---------- */
document.addEventListener("DOMContentLoaded", function(){
  el("presetSelect").innerHTML = presetOptions();
  renderLoads();
  // preselect a common starter set so the tool shows something useful immediately
  addLoad(PRESETS[0].name, PRESETS[0].run, PRESETS[0].surge);
  addLoad(PRESETS[9].name, PRESETS[9].run, PRESETS[9].surge);
});
