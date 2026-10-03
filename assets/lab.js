/* GeneratorSizer Lab — methods other wattage widgets do not run.
   Naive sizers: sum every running watt + the extra of the highest start + 20%.
   This file: staggered-start coincidence, altitude/temp derate, lot-line dBA,
   storm fuel, and portable-vs-standby TCO. Not a substitute for a licensed electrician. */
"use strict";

var GS = window.GS || {};
window.GS = GS;

GS.PRESETS = [
  { name: "Refrigerator (Energy Star)", run: 150, surge: 600, lane: "always" },
  { name: "Chest freezer", run: 200, surge: 600, lane: "always" },
  { name: "Well pump 1/2 HP", run: 1000, surge: 2100, lane: "always" },
  { name: "Sump pump 1/2 HP", run: 800, surge: 1300, lane: "always" },
  { name: "Furnace fan 1/3 HP", run: 700, surge: 1400, lane: "always" },
  { name: "LED lights", run: 80, surge: 80, lane: "always" },
  { name: "Modem + phones", run: 80, surge: 80, lane: "always" },
  { name: "Window AC 10k BTU", run: 900, surge: 1400, lane: "wait" },
  { name: "Central AC 2.5 ton", run: 3500, surge: 5000, lane: "wait" },
  { name: "Microwave", run: 1000, surge: 1000, lane: "never" },
  { name: "Coffee maker", run: 1000, surge: 1000, lane: "never" },
  { name: "Space heater", run: 1500, surge: 1500, lane: "never" },
  { name: "Washing machine", run: 1150, surge: 2300, lane: "wait" }
];

GS.fmt = function (n) { return Math.round(n).toLocaleString("en-US"); };
GS.ceilTo = function (n, step) { return Math.ceil(n / step) * step; };

GS.sumRun = function (rows) {
  return rows.reduce(function (s, r) { return s + (Number(r.run) || 0) * (Number(r.qty) || 1); }, 0);
};

/* Same extra-surge rule as the home calculator: the row with the highest
   starting watts (quantity already multiplied in). Extra = that row's start
   minus its running watts. A tie keeps the first row. */
GS.maxExtra = function (rows) {
  var bestStart = -1;
  var extra = 0;
  rows.forEach(function (r) {
    var q = Number(r.qty) || 1;
    var run = (Number(r.run) || 0) * q;
    var surge = (Number(r.surge) || 0) * q;
    if (surge > bestStart) {
      bestStart = surge;
      extra = Math.max(0, surge - run);
    }
  });
  return extra;
};

/** Naive marketplace math: everything on at once + one largest motor kick. */
GS.naivePeak = function (rows, headroomPct) {
  var hr = 1 + (Number(headroomPct) || 0) / 100;
  return (GS.sumRun(rows) + GS.maxExtra(rows)) * hr;
};

/**
 * Staggered-start coincidence — the Lab difference.
 * always: stay on. wait: start after motors settle. never: kitchen/heat that must not share a motor start.
 * Phase A = always running + the extra of the highest start among always and wait.
 * Phase B = always + wait running, no extra.
 * Phase C = always + never running, no extra.
 */
GS.sequenced = function (rows, headroomPct) {
  var always = rows.filter(function (r) { return r.lane === "always"; });
  var wait = rows.filter(function (r) { return r.lane === "wait"; });
  var never = rows.filter(function (r) { return r.lane === "never"; });
  var hr = 1 + (Number(headroomPct) || 0) / 100;
  var alwaysRun = GS.sumRun(always);
  var waitRun = GS.sumRun(wait);
  var neverRun = GS.sumRun(never);
  var phaseA = alwaysRun + GS.maxExtra(always.concat(wait));
  var phaseB = alwaysRun + waitRun;
  var phaseC = alwaysRun + neverRun;
  var peak = Math.max(phaseA, phaseB, phaseC) * hr;
  var naive = GS.naivePeak(rows, headroomPct);
  return {
    alwaysRun: alwaysRun,
    waitRun: waitRun,
    neverRun: neverRun,
    phaseA: phaseA,
    phaseB: phaseB,
    phaseC: phaseC,
    peak: peak,
    naive: naive,
    saved: Math.max(0, naive - peak),
    buy: GS.ceilTo(peak, 500)
  };
};

/**
 * House curve: no altitude hit through 1,000 ft, then 3.5% per additional 1,000 ft;
 * 1% per 10°F above 77°F inlet air. Floor 55%.
 * Generac GP6500/GP8000E manual: 3.5% per 1,000 ft above sea level, and 1% per 10°F above 60°F.
 */
GS.derateFactor = function (elevFt, tempF) {
  var alt = 0;
  elevFt = Number(elevFt) || 0;
  tempF = Number(tempF) || 77;
  if (elevFt > 1000) alt = 0.035 * ((elevFt - 1000) / 1000);
  var temp = 0;
  if (tempF > 77) temp = 0.01 * ((tempF - 77) / 10);
  return Math.max(0.55, 1 - alt - temp);
};

GS.usableWatts = function (nameplate, elevFt, tempF) {
  return nameplate * GS.derateFactor(elevFt, tempF);
};

/* Oil intervals from the cited owner's manuals. A change uses whichever of the
   hour limit and the calendar limit comes first, then both clocks reset.
   Honda EU2200i maintenance schedule: engine-oil "Change" is in the
   "first month or 20 hours" column and the "every 6 months or 100 hours" column.
   Generac GP6500/GP8000E: change oil after the first 30 hours, then every
   100 hours or every year. firstMonths null means the first change is hours-only.
   The Generac heavy-load monthly footnote is not a field here. */
GS.OIL_SCHEDULES = {
  hondaEU2200i: {
    label: "Honda EU2200i",
    firstHours: 20,
    firstMonths: 1,
    everyHours: 100,
    everyMonths: 6
  },
  generacGP: {
    label: "Generac GP6500 / GP8000E",
    firstHours: 30,
    firstMonths: null,
    everyHours: 100,
    everyMonths: 12
  }
};

GS.oilSchedule = function (id) {
  return GS.OIL_SCHEDULES[id] || GS.OIL_SCHEDULES.hondaEU2200i;
};

/* New-engine window. engineHours are spread evenly across calendarMonths.
   A change exactly at the end of the window counts. */
GS.oilChangesInWindow = function (scheduleId, engineHours, calendarMonths) {
  var sch = GS.oilSchedule(scheduleId);
  engineHours = Math.max(0, Number(engineHours) || 0);
  calendarMonths = Math.max(0, Number(calendarMonths) || 0);
  var hpm = calendarMonths > 0 ? engineHours / calendarMonths : 0;
  var count = 0;
  var month = 0;
  var first = true;
  var guard = 0;
  while (guard++ < 10000) {
    var hourLimit = first ? sch.firstHours : sch.everyHours;
    var monthLimit = first ? sch.firstMonths : sch.everyMonths;
    var next = null;
    if (hourLimit != null && hpm > 0) next = month + (hourLimit / hpm);
    if (monthLimit != null) {
      var cal = month + monthLimit;
      next = next == null ? cal : Math.min(next, cal);
    }
    if (next == null || next > calendarMonths + 1e-6) break;
    count++;
    month = next;
    first = false;
  }
  return count;
};

/* Hour column only, for a window too short for the calendar half.
   Marks are firstHours, then every everyHours after that.
   A mark equal to the starting meter is already done. Marks in (meter, meter+engineHours] count. */
GS.oilHourMarks = function (scheduleId, meterHours, engineHours) {
  var sch = GS.oilSchedule(scheduleId);
  meterHours = Math.max(0, Number(meterHours) || 0);
  engineHours = Math.max(0, Number(engineHours) || 0);
  var end = meterHours + engineHours;
  var next;
  if (meterHours < sch.firstHours) next = sch.firstHours;
  else {
    var n = Math.floor((meterHours - sch.firstHours) / sch.everyHours) + 1;
    next = sch.firstHours + n * sch.everyHours;
  }
  var marks = [];
  var guard = 0;
  while (next <= end + 1e-9 && guard++ < 10000) {
    marks.push(next);
    next += sch.everyHours;
  }
  return marks;
};

GS.oilNextHourMark = function (scheduleId, atHour) {
  var sch = GS.oilSchedule(scheduleId);
  var marks = GS.oilHourMarks(scheduleId, atHour, sch.firstHours + sch.everyHours);
  return marks.length ? marks[0] : null;
};

/** Site fuel rule: ~1 gal gasoline per 7,000 W of *running* load per hour. Propane ~25% more volume. */
GS.galPerHour = function (runningW, fuel) {
  var gas = (Number(runningW) || 0) / 7000;
  return fuel === "propane" ? gas / 0.75 : gas;
};

GS.NOISE_CLASS = {
  inverter22: { label: "Inverter ~2,200 W", dba: 53, refFt: 23 },
  inverter35: { label: "Inverter ~3,500 W", dba: 58, refFt: 23 },
  open75: { label: "Open-frame ~7,500 W", dba: 76, refFt: 23 },
  standby22: { label: "Enclosed standby ~22 kW", dba: 67, refFt: 23 }
};

GS.dbaAt = function (refDba, refFt, distFt, barrierDb) {
  distFt = Math.max(3, Number(distFt) || refFt);
  refFt = Math.max(3, Number(refFt) || 23);
  var spread = 20 * Math.log10(distFt / refFt);
  return (Number(refDba) || 0) - spread - (Number(barrierDb) || 0);
};

GS.tco = function (opt) {
  var runW = Number(opt.runningW) || 2000;
  var outageH = opt.outageHoursYear;
  if (outageH === "" || outageH == null) outageH = 20;
  else outageH = Number(outageH);
  if (!isFinite(outageH) || outageH < 0) outageH = 0;
  var years = Number(opt.years) || 5;
  var gasPrice = Number(opt.gasPrice) || 3.4;
  var portablePrice = Number(opt.portablePrice) || 1200;
  var standbyInstall = Number(opt.standbyInstall) || 12000;
  var standbyService = Number(opt.standbyService) || 280;
  var galHr = GS.galPerHour(runW, "gas");
  var portableFuelYr = galHr * outageH * gasPrice;
  var scheduleId = GS.OIL_SCHEDULES[opt.oilSchedule] ? opt.oilSchedule : "hondaEU2200i";
  var rawOil = opt.oilCostEach;
  var oilEach = 0;
  if (rawOil !== "" && rawOil != null) {
    oilEach = Number(rawOil);
    if (!isFinite(oilEach) || oilEach < 0) oilEach = 0;
  }
  var oilChanges = GS.oilChangesInWindow(scheduleId, outageH * years, years * 12);
  var oilDollars = oilChanges * oilEach;
  var portable5 = portablePrice + portableFuelYr * years + oilDollars;
  var standby5 = standbyInstall + standbyService * years;
  var extraPerHour = gasPrice * galHr;
  var gap = standbyInstall - portablePrice;
  return {
    galHr: galHr,
    portableFuelYr: portableFuelYr,
    oilSchedule: scheduleId,
    oilChanges: oilChanges,
    oilDollars: oilDollars,
    portable5: portable5,
    standby5: standby5,
    cheaper: portable5 <= standby5 ? "portable" : "standby",
    breakEvenHours: extraPerHour > 0 ? gap / extraPerHour : null
  };
};

GS.HOUSE_STACKS = {
  wellRanch: {
    title: "Well-pump ranch (New Auburn pattern)",
    note: "Food + water + heat fan. Sequence the well start away from the microwave.",
    rows: [
      { name: "Fridge", run: 150, surge: 600, qty: 1, lane: "always" },
      { name: "Freezer", run: 200, surge: 600, qty: 1, lane: "always" },
      { name: "Well 1/2 HP", run: 1000, surge: 2100, qty: 1, lane: "always" },
      { name: "Furnace fan", run: 700, surge: 1400, qty: 1, lane: "always" },
      { name: "Lights + comms", run: 160, surge: 160, qty: 1, lane: "always" },
      { name: "Microwave", run: 1000, surge: 1000, qty: 1, lane: "never" }
    ]
  },
  citySump: {
    title: "City bungalow with a sump",
    note: "No well. The sump is the motor that kills cheap inverters.",
    rows: [
      { name: "Fridge", run: 150, surge: 600, qty: 1, lane: "always" },
      { name: "Sump 1/2 HP", run: 800, surge: 1300, qty: 1, lane: "always" },
      { name: "Furnace fan", run: 700, surge: 1400, qty: 1, lane: "always" },
      { name: "Lights + comms", run: 160, surge: 160, qty: 1, lane: "always" },
      { name: "Window AC", run: 900, surge: 1400, qty: 1, lane: "wait" },
      { name: "Coffee + microwave", run: 2000, surge: 2000, qty: 1, lane: "never" }
    ]
  },
  rvWeekend: {
    title: "30-ft travel trailer weekend",
    note: "Roof AC waits until the converter and fridge are already running.",
    rows: [
      { name: "RV fridge (absorb)", run: 350, surge: 600, qty: 1, lane: "always" },
      { name: "Converter / charging", run: 400, surge: 400, qty: 1, lane: "always" },
      { name: "Lights + pump", run: 150, surge: 300, qty: 1, lane: "always" },
      { name: "Roof AC 13.5k", run: 1500, surge: 2800, qty: 1, lane: "wait" },
      { name: "Microwave", run: 1000, surge: 1000, qty: 1, lane: "never" }
    ]
  }
};
