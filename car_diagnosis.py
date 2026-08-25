#!/usr/bin/env python3
"""Car Diagnosis Program - Guided Diagnostic Assistant
Flow: Car details -> Symptom selection -> Diagnosis -> Next steps -> Report
"""

import sqlite3, datetime, json, re, os, time
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
try:
    import serial
    SERIAL_AVAILABLE = True
except Exception:
    SERIAL_AVAILABLE = False

DB_PATH = Path(__file__).with_name("car_diagnosis.db")
CONFIG_PATH = Path(__file__).with_name("car_config.json")
OBD2_PORT = "COM3"
OBD2_BAUD = 38400
OBD2_AUTO = True

OBD2_CODES = {
    "P0171": {"description": "System Too Lean (Bank 1)", "symptoms": ["rough idle","check engine light","poor fuel economy","stalling","hesitation"], "causes": ["vacuum leak","dirty MAF sensor","weak fuel pump","clogged fuel filter","bad O2 sensor"], "repairs": ["Inspect vacuum hoses","Clean/replace MAF","Check fuel pressure","Replace fuel filter","Test upstream O2 sensor"], "cost_estimate": "£50 - £350", "severity": "Medium", "diy": True, "priority": 2},
    "P0172": {"description": "System Too Rich (Bank 1)", "symptoms": ["check engine light","poor fuel economy","black smoke","rough idle"], "causes": ["dirty air filter","failing O2 sensor","fuel pressure regulator failure","injector leak"], "repairs": ["Replace air filter","Test O2 sensor","Check fuel pressure regulator","Inspect injectors"], "cost_estimate": "£40 - £300", "severity": "Medium", "diy": True, "priority": 2},
    "P0300": {"description": "Random/Multiple Cylinder Misfire", "symptoms": ["misfire","rough idle","check engine light","loss of power","vibration","shaking"], "causes": ["worn spark plugs","bad ignition coils","low compression","vacuum leak","bad fuel"], "repairs": ["Replace spark plugs","Test ignition coils","Compression test","Check vacuum leaks"], "cost_estimate": "£80 - £600", "severity": "High", "diy": True, "priority": 1},
    "P0301": {"description": "Cylinder 1 Misfire", "symptoms": ["misfire","rough idle","check engine light","vibration"], "causes": ["worn plug cylinder 1","ignition coil failure","low compression","injector fault"], "repairs": ["Replace spark plug cylinder 1","Test ignition coil","Compression test"], "cost_estimate": "£50 - £400", "severity": "High", "diy": True, "priority": 1},
    "P0302": {"description": "Cylinder 2 Misfire", "symptoms": ["misfire","rough idle","check engine light","vibration"], "causes": ["worn plug cylinder 2","ignition coil failure","low compression","injector fault"], "repairs": ["Replace spark plug cylinder 2","Test ignition coil","Compression test"], "cost_estimate": "£50 - £400", "severity": "High", "diy": True, "priority": 1},
    "P0303": {"description": "Cylinder 3 Misfire", "symptoms": ["misfire","rough idle","check engine light","vibration"], "causes": ["worn plug cylinder 3","ignition coil failure","low compression","injector fault"], "repairs": ["Replace spark plug cylinder 3","Test ignition coil","Compression test"], "cost_estimate": "£50 - £400", "severity": "High", "diy": True, "priority": 1},
    "P0304": {"description": "Cylinder 4 Misfire", "symptoms": ["misfire","rough idle","check engine light","vibration"], "causes": ["worn plug cylinder 4","ignition coil failure","low compression","injector fault"], "repairs": ["Replace spark plug cylinder 4","Test ignition coil","Compression test"], "cost_estimate": "£50 - £400", "severity": "High", "diy": True, "priority": 1},
    "P0420": {"description": "Catalyst Efficiency Below Threshold (Bank 1)", "symptoms": ["check engine light","failed emissions","sulfur smell","poor performance"], "causes": ["failed catalytic converter","bad O2 sensor","exhaust leak","misfire damage"], "repairs": ["Replace catalytic converter","Test/replace O2 sensors","Check exhaust leaks","Fix misfire first"], "cost_estimate": "£200 - £1,200", "severity": "High", "diy": False, "priority": 1},
    "P0430": {"description": "Catalyst Efficiency Below Threshold (Bank 2)", "symptoms": ["check engine light","failed emissions","sulfur smell"], "causes": ["failed converter bank 2","bad O2 sensor bank 2","exhaust leak"], "repairs": ["Replace catalytic converter bank 2","Test/replace O2 sensors","Check exhaust leaks"], "cost_estimate": "£200 - £1,200", "severity": "High", "diy": False, "priority": 1},
    "P0128": {"description": "Coolant Thermostat Below Regulating Temp", "symptoms": ["engine running cold","poor heater","check engine light","poor fuel economy"], "causes": ["stuck open thermostat","low coolant","failed temp sensor","water pump issue"], "repairs": ["Replace thermostat","Check coolant level","Test temp sensor","Inspect water pump"], "cost_estimate": "£80 - £350", "severity": "Medium", "diy": True, "priority": 3},
    "P0135": {"description": "O2 Sensor Heater Circuit (Bank 1 Sensor 1)", "symptoms": ["check engine light","poor cold idle","emissions failure"], "causes": ["failed O2 heater","wiring damage","blown fuse","ECM fault"], "repairs": ["Replace O2 sensor","Check wiring/fuse","Test ECM driver"], "cost_estimate": "£60 - £250", "severity": "Medium", "diy": True, "priority": 3},
    "P0141": {"description": "O2 Sensor Heater Circuit (Bank 1 Sensor 2)", "symptoms": ["check engine light","catalyst damage risk"], "causes": ["failed rear O2 heater","wiring damage","blown fuse"], "repairs": ["Replace downstream O2 sensor","Check wiring","Test fuses"], "cost_estimate": "£60 - £250", "severity": "Medium", "diy": True, "priority": 3},
    "P0340": {"description": "Camshaft Position Sensor Circuit", "symptoms": ["check engine light","hard start","stalling","poor performance","no start"], "causes": ["failed CMP sensor","wiring damage","timing belt/chain stretch","oil contamination"], "repairs": ["Replace camshaft position sensor","Check wiring harness","Inspect timing belt/chain","Clean oil contamination"], "cost_estimate": "£70 - £400", "severity": "High", "diy": True, "priority": 1},
    "P0351": {"description": "Ignition Coil A Circuit Malfunction", "symptoms": ["misfire","check engine light","hard start","rough idle","backfire"], "causes": ["failed ignition coil","wiring damage","failing ICM","spark plug wire damage"], "repairs": ["Replace ignition coil","Test wiring/connectors","Check ICM","Replace plug wires if needed"], "cost_estimate": "£60 - £350", "severity": "High", "diy": True, "priority": 1},
    "P0401": {"description": "EGR Flow Insufficient", "symptoms": ["check engine light","rough idle","pinging","poor fuel economy","emissions fail"], "causes": ["clogged EGR","faulty EGR solenoid","carbon buildup","vacuum leak"], "repairs": ["Clean/replace EGR valve","Test solenoid","Clean intake manifold","Check vacuum lines"], "cost_estimate": "£80 - £450", "severity": "Medium", "diy": True, "priority": 2},
    "P0505": {"description": "Idle Air Control System Malfunction", "symptoms": ["rough idle","stalling","high idle","check engine light","idle hunting"], "causes": ["dirty IAC valve","failing throttle body","vacuum leak","ECM idle fault"], "repairs": ["Clean IAC valve","Clean throttle body","Check vacuum leaks","Throttle body relearn"], "cost_estimate": "£50 - £300", "severity": "Medium", "diy": True, "priority": 2},
    "P0562": {"description": "System Voltage Low", "symptoms": ["check engine light","dim lights","slow cranking","battery warning light","electrical issues"], "causes": ["failing alternator","bad battery","corroded terminals","voltage regulator failure","parasitic drain"], "repairs": ["Test alternator output","Load test battery","Clean terminals","Check for parasitic draw"], "cost_estimate": "£80 - £500", "severity": "High", "diy": True, "priority": 1},
    "P0700": {"description": "Transmission Control System Malfunction", "symptoms": ["check engine light","harsh shifting","slipping gears","limp mode","won't shift"], "causes": ["faulty TCM","wiring/connector issue","low transmission fluid","solenoid failure","valve body issue"], "repairs": ["Scan for TCM-specific codes","Check transmission fluid","Test solenoids","Check TCM wiring"], "cost_estimate": "£100 - £1,500", "severity": "High", "diy": False, "priority": 1},
    "C0035": {"description": "Left Front Wheel Speed Sensor Circuit", "symptoms": ["ABS light","ESC light","speedometer inaccurate","traction control disabled"], "causes": ["failed wheel speed sensor","damaged sensor ring","wiring damage","ABS module fault"], "repairs": ["Replace wheel speed sensor","Inspect sensor ring","Check wiring harness","Test ABS module"], "cost_estimate": "£60 - £300", "severity": "Medium", "diy": True, "priority": 3},
    "B0001": {"description": "Driver Frontal Stage Squib Circuit Open", "symptoms": ["airbag warning light","SRS light"], "causes": ["failed airbag squib","clockspring failure","wiring damage","airbag module fault"], "repairs": ["Replace squib/clockspring","Check wiring","Scan airbag module","Reset SRS system"], "cost_estimate": "£150 - £800", "severity": "High", "diy": False, "priority": 1},
    "U0100": {"description": "Lost Communication With ECM/PCM A", "symptoms": ["check engine light","multiple warning lights","no-start","limp mode"], "causes": ["CAN bus wiring damage","failed ECM/PCM","ground fault","module failure"], "repairs": ["Inspect CAN bus wiring","Check grounds","Test ECM/PCM communication","Replace module if needed"], "cost_estimate": "£100 - £1,000", "severity": "High", "diy": False, "priority": 1},
    "P0010": {"description": "'A' Camshaft Position Actuator Circuit (Bank 1)", "symptoms": ["rough idle","check engine light","poor fuel economy","hard start"], "causes": ["failed cam actuator solenoid","low oil pressure","timing chain stretch","wiring damage"], "repairs": ["Replace cam actuator solenoid","Check oil pressure","Inspect timing chain","Clear VVT screens"], "cost_estimate": "£100 - £600", "severity": "High", "diy": False, "priority": 1},
    "P0016": {"description": "CKP - CMP Correlation (Bank 1)", "symptoms": ["check engine light","hard start","stalling","rough idle","no start"], "causes": ["timing belt/chain jumped","failed CKP sensor","failed CMP sensor","low oil pressure"], "repairs": ["Check valve timing","Replace CKP/CMP sensors","Verify oil pressure","Check timing marks"], "cost_estimate": "£150 - £900", "severity": "High", "diy": False, "priority": 1},
    "P0120": {"description": "Throttle Position Sensor/Switch A Circuit", "symptoms": ["check engine light","poor throttle response","rough idle","stalling"], "causes": ["failed TPS","wiring damage","throttle body failure","misadjusted TPS"], "repairs": ["Replace TPS","Check throttle body wiring","Throttle body relearn","Verify voltage sweep"], "cost_estimate": "£50 - £250", "severity": "Medium", "diy": True, "priority": 2},
    "P0220": {"description": "Throttle/Pedal Position Sensor B Circuit", "symptoms": ["poor throttle response","check engine light","limp mode"], "causes": ["failed pedal position sensor","wiring damage","throttle body failure"], "repairs": ["Replace pedal position sensor","Check wiring","Throttle body relearn"], "cost_estimate": "£60 - £300", "severity": "Medium", "diy": True, "priority": 2},
    "P0299": {"description": "Turbocharger Underboost", "symptoms": ["loss of power","check engine light","poor acceleration","turbo whine"], "causes": ["worn turbo","wastegate stuck","boost leak","clogged intake","MAP/MAF fault"], "repairs": ["Inspect turbo/wastegate","Pressure test for boost leaks","Clean/replace MAP/MAF","Check intercooler"], "cost_estimate": "£100 - £1,000", "severity": "High", "diy": False, "priority": 1},
    "P0335": {"description": "Crankshaft Position Sensor Circuit", "symptoms": ["no start","hard start","stalling","check engine light","loss of power"], "causes": ["failed CKP sensor","wiring damage","missing reluctor wheel teeth","timing belt/chain issue"], "repairs": ["Replace crankshaft position sensor","Check wiring harness","Inspect reluctor wheel","Verify timing marks"], "cost_estimate": "£70 - £400", "severity": "High", "diy": False, "priority": 1},
    "P0400": {"description": "EGR Flow Malfunction", "symptoms": ["check engine light","rough idle","pinging","poor fuel economy"], "causes": ["clogged EGR valve","faulty EGR solenoid","carbon buildup","vacuum leak"], "repairs": ["Clean/replace EGR valve","Test EGR solenoid","Clean intake carbon","Check vacuum lines"], "cost_estimate": "£80 - £450", "severity": "Medium", "diy": True, "priority": 2},
    "P0440": {"description": "EVAP System Malfunction", "symptoms": ["check engine light","fuel smell","emissions fail"], "causes": ["leaking EVAP hose","failed purge valve","failed vent valve","loose gas cap"], "repairs": ["Inspect EVAP hoses","Replace purge/vent valves","Tighten gas cap","Smoke test EVAP"], "cost_estimate": "£30 - £250", "severity": "Low", "diy": True, "priority": 3},
    "P0442": {"description": "EVAP System Small Leak", "symptoms": ["check engine light","fuel smell"], "causes": ["small EVAP leak","loose gas cap","cracked hose","failed purge valve"], "repairs": ["Tighten/replace gas cap","Inspect hoses","Smoke test EVAP","Replace purge valve if needed"], "cost_estimate": "£30 - £200", "severity": "Low", "diy": True, "priority": 3},
    "P0506": {"description": "Idle Speed Lower Than Expected", "symptoms": ["low idle","stalling","rough idle"], "causes": ["dirty IAC valve","vacuum leak","throttle body issue","ECM fault"], "repairs": ["Clean IAC valve","Check for vacuum leaks","Throttle body relearn","Scan for additional codes"], "cost_estimate": "£50 - £250", "severity": "Medium", "diy": True, "priority": 2},
    "P0507": {"description": "Idle Speed Higher Than Expected", "symptoms": ["high idle","rough idle","check engine light"], "causes": ["IAC valve stuck open","vacuum leak","throttle body sticking","ECM fault"], "repairs": ["Clean/replace IAC valve","Check for vacuum leaks","Clean throttle body","Throttle body relearn"], "cost_estimate": "£50 - £250", "severity": "Medium", "diy": True, "priority": 2},
    "P0520": {"description": "Engine Oil Pressure Sensor Circuit", "symptoms": ["oil pressure warning","check engine light","low oil pressure reading"], "causes": ["failed oil pressure sensor","wiring damage","low oil level","pump failure"], "repairs": ["Replace oil pressure sensor","Check oil level/condition","Verify pump pressure"], "cost_estimate": "£50 - £250", "severity": "High", "diy": True, "priority": 1},
    "P0605": {"description": "Internal Control Module ROM Error", "symptoms": ["check engine light","no-start","intermittent electrical issues"], "causes": ["failed ECM/PCM","corrupted firmware","power supply fault"], "repairs": ["Reflash/replace ECM/PCM","Check power/ground to module","Verify software version"], "cost_estimate": "£150 - £1,200", "severity": "High", "diy": False, "priority": 1},
    "P0650": {"description": "MIL Circuit Malfunction", "symptoms": ["MIL stuck on/off","no MIL operation"], "causes": ["failed MIL bulb/LED","wiring damage","ECM fault","cluster failure"], "repairs": ["Check MIL bulb/LED","Test wiring","Scan ECM","Test cluster"], "cost_estimate": "£30 - £300", "severity": "Low", "diy": True, "priority": 3},
    "P0705": {"description": "Transmission Range Sensor Circuit", "symptoms": ["won't start in gear","wrong gear indicator","harsh shifts","limp mode"], "causes": ["failed range sensor","wiring damage","adjustment needed","TCM fault"], "repairs": ["Replace transmission range sensor","Check wiring","Adjust sensor position","Scan TCM"], "cost_estimate": "£80 - £350", "severity": "High", "diy": False, "priority": 1},
    "P0725": {"description": "Engine Speed Input Circuit", "symptoms": ["harsh shifting","erratic speedometer","check engine light","limp mode"], "causes": ["failed CKP sensor","wiring damage","ECM signal fault"], "repairs": ["Replace CKP sensor","Check wiring","Verify ECM signal"], "cost_estimate": "£70 - £400", "severity": "High", "diy": False, "priority": 1},
    "P0741": {"description": "Torque Converter Clutch Circuit Performance", "symptoms": ["slipping","harsh engagement","check engine light","poor fuel economy"], "causes": ["TCC solenoid failure","wiring damage","TC clutch wear","low fluid"], "repairs": ["Replace TCC solenoid","Check wiring","Test torque converter","Check fluid"], "cost_estimate": "£120 - £700", "severity": "Medium", "diy": False, "priority": 2},
    "P0755": {"description": "Shift Solenoid B Malfunction", "symptoms": ["harsh shifting","slipping","check engine light","limp mode"], "causes": ["failed shift solenoid B","wiring damage","low transmission fluid","valve body wear"], "repairs": ["Replace shift solenoid B","Check wiring","Change transmission fluid","Inspect valve body"], "cost_estimate": "£120 - £600", "severity": "High", "diy": False, "priority": 1},
    "P0771": {"description": "Shift Solenoid E Malfunction", "symptoms": ["harsh shifting","slipping","check engine light","limp mode"], "causes": ["failed shift solenoid E","wiring damage","low transmission fluid"], "repairs": ["Replace shift solenoid E","Check wiring","Check fluid level/condition"], "cost_estimate": "£120 - £600", "severity": "High", "diy": False, "priority": 1},
    "P0xxx": {"description": "Generic Powertrain Code", "symptoms": ["check engine light","unknown symptom"], "causes": ["various - use OBD2 scanner for specific code"], "repairs": ["Read exact code with OBD2 scanner","Consult specific code database","Check freeze frame data"], "cost_estimate": "Varies", "severity": "Unknown", "diy": True, "priority": 4},
    "P0016": {"description": "CKP - CMP Correlation (Bank 1)", "symptoms": ["check engine light","hard start","stalling","rough idle","no start"], "causes": ["timing belt/chain jumped","failed CKP sensor","failed CMP sensor","low oil pressure"], "repairs": ["Check valve timing","Replace CKP/CMP sensors","Verify oil pressure","Check timing marks"], "cost_estimate": "£150 - £900", "severity": "High", "diy": False, "priority": 1},
    "P0110": {"description": "Intake Air Temperature Sensor Circuit", "symptoms": ["check engine light","poor fuel economy","rough idle"], "causes": ["failed IAT sensor","wiring damage","connector corrosion"], "repairs": ["Replace IAT sensor","Check wiring/connector","Clear codes and monitor"], "cost_estimate": "£30 - £150", "severity": "Low", "diy": True, "priority": 3},
    "P0115": {"description": "Engine Coolant Temperature Circuit", "symptoms": ["check engine light","poor heater","rich running","hard start cold"], "causes": ["failed coolant temp sensor","wiring damage","ECM fault"], "repairs": ["Replace coolant temp sensor","Check wiring","Verify ECU voltage reference"], "cost_estimate": "£40 - £200", "severity": "Medium", "diy": True, "priority": 3},
    "P0325": {"description": "Knock Sensor Circuit (Bank 1)", "symptoms": ["check engine light","pinging/knocking","poor performance","high idle"], "causes": ["failed knock sensor","wiring damage","ECM fault","detonation damage"], "repairs": ["Replace knock sensor","Check wiring","Verify ECM input","Inspect for detonation damage"], "cost_estimate": "£60 - £300", "severity": "Medium", "diy": True, "priority": 2},
    "P0327": {"description": "Knock Sensor Circuit Low Input (Bank 1)", "symptoms": ["pinging/knocking","check engine light","poor performance"], "causes": ["failed knock sensor","wiring damage","ECM fault"], "repairs": ["Replace knock sensor","Check wiring","Test ECM input"], "cost_estimate": "£60 - £300", "severity": "Medium", "diy": True, "priority": 2},
    "P0336": {"description": "Crankshaft Position Sensor A Range/Performance", "symptoms": ["no start","hard start","stalling","check engine light"], "causes": ["failed CKP sensor","air gap too large","wiring damage"], "repairs": ["Replace CKP sensor","Check air gap","Verify mounting"], "cost_estimate": "£70 - £400", "severity": "High", "diy": False, "priority": 1},
    "P0341": {"description": "Camshaft Position Sensor Range/Performance", "symptoms": ["hard start","check engine light","stalling"], "causes": ["failed CMP sensor","timing misalignment","wiring damage"], "repairs": ["Replace CMP sensor","Verify timing alignment","Check wiring"], "cost_estimate": "£70 - £400", "severity": "High", "diy": True, "priority": 1},
    "P0352": {"description": "Ignition Coil B Circuit Malfunction", "symptoms": ["misfire","check engine light","hard start","rough idle"], "causes": ["failed ignition coil B","wiring damage","failing ICM"], "repairs": ["Replace ignition coil B","Test wiring/connectors","Check ICM"], "cost_estimate": "£60 - £350", "severity": "High", "diy": True, "priority": 1},
    "P0353": {"description": "Ignition Coil C Circuit Malfunction", "symptoms": ["misfire","check engine light","hard start","rough idle"], "causes": ["failed ignition coil C","wiring damage","failing ICM"], "repairs": ["Replace ignition coil C","Test wiring/connectors","Check ICM"], "cost_estimate": "£60 - £350", "severity": "High", "diy": True, "priority": 1},
    "P0402": {"description": "EGR Flow Excessive", "symptoms": ["check engine light","rough idle","stalling","emissions fail"], "causes": ["EGR stuck open","faulty EGR solenoid","carbon buildup","vacuum leak"], "repairs": ["Clean/replace EGR valve","Test solenoid","Check vacuum lines","Inspect EGR ports"], "cost_estimate": "£80 - £450", "severity": "Medium", "diy": True, "priority": 2},
    "P0403": {"description": "EGR Control Circuit Malfunction", "symptoms": ["check engine light","rough idle","pinging","emissions fail"], "causes": ["failed EGR solenoid","wiring damage","ECM driver fault"], "repairs": ["Replace EGR solenoid","Check wiring/connector","Test ECM driver"], "cost_estimate": "£60 - £300", "severity": "Medium", "diy": True, "priority": 2},
    "P0410": {"description": "Secondary Air Injection System Malfunction", "symptoms": ["check engine light","emissions failure","cold start issues"], "causes": ["failed air pump","failed diverter valve","wiring damage","vacuum leak"], "repairs": ["Replace air pump","Replace diverter valve","Check wiring/vacuum lines"], "cost_estimate": "£80 - £450", "severity": "Medium", "diy": False, "priority": 2},
    "P0411": {"description": "Secondary Air Injection Incorrect Flow", "symptoms": ["check engine light","emissions fail"], "causes": ["air pump failure","blocked air lines","failed diverter valve"], "repairs": ["Inspect air pump","Check air lines","Replace diverter valve"], "cost_estimate": "£80 - £450", "severity": "Medium", "diy": False, "priority": 2},
    "P0443": {"description": "EVAP Purge Control Valve Circuit", "symptoms": ["check engine light","rough idle","failed emissions"], "causes": ["failed purge valve","wiring damage","ECM fault"], "repairs": ["Replace purge valve","Check wiring","Test ECM control"], "cost_estimate": "£40 - £180", "severity": "Medium", "diy": True, "priority": 3},
    "P0446": {"description": "EVAP Vent Control Circuit", "symptoms": ["check engine light","poor fuel economy","failed emissions"], "causes": ["failed vent valve","blocked vent hose","wiring damage"], "repairs": ["Replace vent valve","Check vent hose for blockage","Inspect wiring"], "cost_estimate": "£40 - £180", "severity": "Medium", "diy": True, "priority": 3},
    "P0500": {"description": "Vehicle Speed Sensor Circuit", "symptoms": ["speedometer inop","harsh shifting","check engine light","cruise control failure"], "causes": ["failed VSS","wiring damage","failed ECM/PCM"], "repairs": ["Replace vehicle speed sensor","Check wiring","Test ECM input"], "cost_estimate": "£70 - £400", "severity": "Medium", "diy": False, "priority": 3},
    "P0501": {"description": "Vehicle Speed Sensor Range/Performance", "symptoms": ["erratic speedometer","harsh shifting","check engine light"], "causes": ["failed VSS","incorrect tone ring","wiring damage"], "repairs": ["Replace VSS","Inspect tone ring","Check wiring"], "cost_estimate": "£70 - £400", "severity": "Medium", "diy": False, "priority": 3},
    "P0600": {"description": "Serial Communication Link Malfunction", "symptoms": ["check engine light","multiple warning lights","gauge cluster issues","limp mode"], "causes": ["CAN bus wiring damage","failed ECM/PCM","ground fault","module failure"], "repairs": ["Inspect CAN bus wiring","Check grounds","Scan for module comm errors","Replace ECM/PCM if needed"], "cost_estimate": "£100 - £800", "severity": "High", "diy": False, "priority": 1},
    "P0606": {"description": "ECM/PCM Processor A Malfunction", "symptoms": ["check engine light","intermittent stalling","no-start","multiple warning lights"], "causes": ["failed ECM/PCM","corrupted software","power/ground issue"], "repairs": ["Reflash or replace ECM/PCM","Check power and ground straps","Verify software version"], "cost_estimate": "£150 - £1,200", "severity": "High", "diy": False, "priority": 1},
    "P0610": {"description": "Control Module Vehicle Options Error", "symptoms": ["check engine light","limp mode","transmission issues"], "causes": ["ECM mismatch after swap","corrupted VIN info","failed ECM"], "repairs": ["Re-program ECM with correct VIN","Verify vehicle options","Replace ECM if corrupted"], "cost_estimate": "£100 - £800", "severity": "High", "diy": False, "priority": 1},
    "P0001": {"description": "Fuel Volume Regulator Control Circuit/Open", "symptoms": ["no start","hard start","rough idle","check engine light"], "causes": ["failed fuel regulator","wiring damage","ECM fault"], "repairs": ["Test fuel volume regulator","Check wiring/connector","Scan for ECM codes"], "cost_estimate": "£80 - £400", "severity": "High", "diy": False, "priority": 1},
    "P0030": {"description": "HO2S Heater Control Circuit (Bank 1 Sensor 1)", "symptoms": ["check engine light","poor fuel economy","rough idle cold"], "causes": ["failed O2 heater","wiring damage","blown fuse","ECM driver fault"], "repairs": ["Replace upstream O2 sensor","Check wiring/fuse","Test ECM driver"], "cost_estimate": "£60 - £250", "severity": "Medium", "diy": True, "priority": 3},
    "P0380": {"description": "Glow Plug/Heater Circuit Malfunction", "symptoms": ["hard start cold","check engine light","rough idle when cold","white smoke"], "causes": ["failed glow plug","glow plug relay failure","wiring damage","bad timer module"], "repairs": ["Replace glow plug(s)","Test glow plug relay/module","Check wiring"], "cost_estimate": "£50 - £250", "severity": "Medium", "diy": True, "priority": 3},
    "P0422": {"description": "Catalyst Efficiency Below Threshold (Bank 1 specific)", "symptoms": ["check engine light","failed emissions","sulfur smell"], "causes": ["converter degradation","O2 sensor drift","exhaust leak"], "repairs": ["Replace converter","Verify O2 sensor activity","Check for exhaust leaks"], "cost_estimate": "£200 - £1,200", "severity": "High", "diy": False, "priority": 1},
    "P0461": {"description": "Fuel Level Sensor Circuit", "symptoms": ["wrong fuel gauge reading","check engine light"], "causes": ["failed fuel level sender","wiring damage","floater stuck"], "repairs": ["Replace fuel level sender","Check wiring","Inspect floater mechanism"], "cost_estimate": "£60 - £350", "severity": "Low", "diy": False, "priority": 3},
}

ALL_SYMPTOMS = sorted(set(s for d in OBD2_CODES.values() for s in d["symptoms"]))

MAINTENANCE_SCHEDULE = [
    ("Oil & Filter", "Every 12 months / 12,000 miles", "£60 - £120", "DIY if under vehicle easily"),
    ("Air Filter", "Every 24 months / 24,000 miles", "£20 - £50", "DIY"),
    ("Cabin Filter", "Every 12 months", "£25 - £60", "DIY"),
    ("Brake Fluid", "Every 24 months", "£40 - £80", "DIY bleed possible"),
    ("Coolant", "Every 60 months", "£60 - £120", "Garage"),
    ("Spark Plugs", "Every 30,000-60,000 miles", "£40 - £160", "DIY for most"),
    ("Timing Belt", "Every 60,000-100,000 miles", "£300 - £800", "Garage"),
    ("Tyres", "Every 5-10 years or 3mm tread", "£60 - £120/tyre", "Garage fit"),
    ("Brake Pads", "Every 30,000-70,000 miles", "£80 - £250", "DIY possible"),
    ("Brake Discs", "As needed with pads", "£150 - £400", "Garage"),
    ("Battery", "Every 3-5 years", "£100 - £220", "DIY"),
    ("Wiper Blades", "Every 12 months", "£15 - £40", "DIY"),
]


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS diagnosis_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        vehicle TEXT,
        code TEXT,
        symptom TEXT,
        result TEXT,
        notes TEXT
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS service_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        mileage INTEGER,
        item TEXT NOT NULL,
        garage TEXT,
        cost REAL,
        notes TEXT
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS mot_tax (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,
        expiry TEXT NOT NULL,
        notified INTEGER NOT NULL DEFAULT 0
    )""")
    conn.commit()
    conn.close()


def log_diagnosis(vehicle=None, symptom=None, result=None, notes=None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO diagnosis_log (timestamp, vehicle, symptom, result, notes) VALUES (?, ?, ?, ?, ?)",
                (datetime.datetime.now().isoformat(), vehicle, symptom, result, notes))
    conn.commit()
    conn.close()


def add_service(date_str, mileage, item, garage="", cost="", notes=""):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO service_log (date, mileage, item, garage, cost, notes) VALUES (?, ?, ?, ?, ?, ?)",
                (date_str, mileage, item, garage, cost, notes))
    conn.commit()
    conn.close()


def delete_service(service_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM service_log WHERE id = ?", (service_id,))
    conn.commit()
    conn.close()


def get_service_log():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, date, mileage, item, garage, cost, notes FROM service_log ORDER BY date DESC")
    rows = cur.fetchall()
    conn.close()
    return rows


def add_mot_tax(expiry_type, expiry_date):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO mot_tax (type, expiry) VALUES (?, ?)", (expiry_type, expiry_date))
    conn.commit()
    conn.close()


def delete_mot_tax(mot_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM mot_tax WHERE id = ?", (mot_id,))
    conn.commit()
    conn.close()


def get_mot_tax():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, type, expiry, notified FROM mot_tax ORDER BY expiry ASC")
    rows = cur.fetchall()
    conn.close()
    return rows


def load_config():
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text())
        except Exception:
            pass
    return {"make": "", "model": "", "year": "", "engine": "", "mileage": "", "vin": ""}


def save_config(cfg):
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2))


def diagnose_by_symptom(symptom_text):
    symptom_lower = symptom_text.strip().lower()
    matches = {}
    for code, data in OBD2_CODES.items():
        for sym in data["symptoms"]:
            if symptom_lower in sym.lower() or sym.lower() in symptom_lower:
                if code not in matches:
                    matches[code] = data
                break
    words = re.findall(r"[a-z]+", symptom_lower)
    for word in words:
        if len(word) > 2:
            for code, data in OBD2_CODES.items():
                for sym in data["symptoms"]:
                    if word in sym.lower():
                        if code not in matches:
                            matches[code] = data
                        break
    return dict(sorted(matches.items(), key=lambda x: (x[1].get("priority", 9), x[0])))


def lookup_code(code):
    code_upper = code.strip().upper()
    if code_upper in OBD2_CODES:
        return code_upper, OBD2_CODES[code_upper]
    for prefix in ["P0", "P1", "P2", "P3", "C0", "B0", "U0"]:
        if code_upper.startswith(prefix):
            if "P0xxx" in OBD2_CODES:
                return "P0xxx", OBD2_CODES["P0xxx"]
    return None, None


class CarDiagnosisApp:
    def __init__(self, root):
        self.root = root
        root.title("Car Diagnosis Assistant")
        root.geometry("920x720")
        root.minsize(760, 560)

        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_wizard = ttk.Frame(self.notebook)
        self.tab_codes = ttk.Frame(self.notebook)
        self.tab_obd2 = ttk.Frame(self.notebook)
        self.tab_service = ttk.Frame(self.notebook)
        self.tab_mot_tax = ttk.Frame(self.notebook)
        self.tab_maintenance = ttk.Frame(self.notebook)
        self.tab_history = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_wizard, text="Diagnose")
        self.notebook.add(self.tab_codes, text="Code Browser")
        self.notebook.add(self.tab_obd2, text="OBD2 Adapter")
        self.notebook.add(self.tab_service, text="Service History")
        self.notebook.add(self.tab_mot_tax, text="MOT / Tax")
        self.notebook.add(self.tab_maintenance, text="Maintenance")
        self.notebook.add(self.tab_history, text="History")

        self.config = load_config()
        self.selected_symptoms = []
        self._build_wizard_tab()
        self._build_codes_tab()
        self._build_obd2_tab()
        self._build_service_tab()
        self._build_mot_tax_tab()
        self._build_maintenance_tab()
        self._build_history_tab()
        self._refresh_history()
        self._refresh_service()
        self._refresh_mot_tax()

    def _build_wizard_tab(self):
        container = ttk.Frame(self.tab_wizard)
        container.pack(fill="both", expand=True)

        # Step 1
        self.step1 = ttk.LabelFrame(container, text="Step 1: Your Vehicle")
        self.step1.pack(fill="x", padx=12, pady=(12, 8))

        row = ttk.Frame(self.step1)
        row.pack(fill="x", padx=8, pady=6)
        ttk.Label(row, text="Make*").pack(side="left")
        self.veh_make = ttk.Entry(row, width=18)
        self.veh_make.pack(side="left", padx=(8, 0))
        ttk.Label(row, text="Model*").pack(side="left", padx=(16, 0))
        self.veh_model = ttk.Entry(row, width=18)
        self.veh_model.pack(side="left", padx=(8, 0))
        ttk.Label(row, text="Year*").pack(side="left", padx=(16, 0))
        self.veh_year = ttk.Entry(row, width=10)
        self.veh_year.pack(side="left", padx=(8, 0))
        ttk.Label(row, text="Engine").pack(side="left", padx=(16, 0))
        self.veh_engine = ttk.Entry(row, width=14)
        self.veh_engine.pack(side="left", padx=(8, 0))

        row2 = ttk.Frame(self.step1)
        row2.pack(fill="x", padx=8, pady=(0, 8))
        ttk.Label(row2, text="Mileage").pack(side="left")
        self.veh_mileage = ttk.Entry(row2, width=14)
        self.veh_mileage.pack(side="left", padx=(8, 0))
        ttk.Label(row2, text="VIN (optional)").pack(side="left", padx=(16, 0))
        self.veh_vin = ttk.Entry(row2, width=24)
        self.veh_vin.pack(side="left", padx=(8, 0))

        self._load_vehicle()

        # Step 2
        self.step2 = ttk.LabelFrame(container, text="Step 2: What’s it doing?")
        self.step2.pack(fill="x", padx=12, pady=8)

        ttk.Label(self.step2, text="Pick all that apply:").pack(anchor="w", padx=8, pady=(8, 4))
        symptom_grid = ttk.Frame(self.step2)
        symptom_grid.pack(fill="x", padx=8, pady=(0, 8))

        self.symptom_vars = {}
        cols = 4
        for idx, sym in enumerate(ALL_SYMPTOMS):
            var = tk.BooleanVar(value=False)
            chk = ttk.Checkbutton(symptom_grid, text=sym.replace("_", " "), variable=var, command=self._sync_symptoms)
            chk.grid(row=idx // cols, column=idx % cols, sticky="w", padx=4, pady=2)
            self.symptom_vars[sym] = var

        ttk.Label(self.step2, text="Or describe it yourself:").pack(anchor="w", padx=8, pady=(4, 4))
        row = ttk.Frame(self.step2)
        row.pack(fill="x", padx=8, pady=(0, 10))
        self.custom_symptom = ttk.Entry(row, font=("Segoe UI", 11))
        self.custom_symptom.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.custom_symptom.bind("<Return>", lambda e: self._run_diagnosis())
        ttk.Button(row, text="Diagnose", command=self._run_diagnosis).pack(side="left")

        # Step 3
        self.step3 = ttk.LabelFrame(container, text="Step 3: Diagnosis")
        self.step3.pack(fill="both", expand=True, padx=12, pady=(8, 12))

        top = ttk.Frame(self.step3)
        top.pack(fill="x", padx=8, pady=(8, 4))
        ttk.Label(top, text="Possible causes — start from the top:", font=("Segoe UI", 11, "bold")).pack(side="left")
        ttk.Button(top, text="Print Report", command=self._print_report).pack(side="right", padx=(0, 8))
        ttk.Button(top, text="Export Report", command=self._export_report).pack(side="right")

        self.result_text = scrolledtext.ScrolledText(self.step3, wrap=tk.WORD, font=("Consolas", 10), height=18)
        self.result_text.pack(fill="both", expand=True, padx=8, pady=(4, 8))

    def _build_maintenance_tab(self):
        frame = ttk.Frame(self.tab_maintenance)
        frame.pack(fill="both", expand=True, padx=12, pady=12)
        ttk.Label(frame, text="Routine Maintenance Tracker", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 8))
        columns = ("item", "interval", "cost", "type")
        self.maint_tree = ttk.Treeview(frame, columns=columns, show="headings", height=18)
        for col, heading in zip(columns, ["Item", "Interval", "Est. Cost", "DIY / Garage"]):
            self.maint_tree.heading(col, text=heading)
            self.maint_tree.column(col, width=220 if col == "item" else 160, anchor="w")
        self.maint_tree.pack(fill="both", expand=True)
        for item, interval, cost, note in MAINTENANCE_SCHEDULE:
            self.maint_tree.insert("", "end", values=(item, interval, cost, note))

    def _build_history_tab(self):
        frame = ttk.Frame(self.tab_history)
        frame.pack(fill="both", expand=True, padx=12, pady=12)
        btns = ttk.Frame(frame)
        btns.pack(fill="x", pady=(0, 10))
        ttk.Button(btns, text="Refresh", command=self._refresh_history).pack(side="left")
        ttk.Button(btns, text="Clear History", command=self._clear_history).pack(side="left", padx=8)
        ttk.Button(btns, text="Export History CSV", command=self._export_history).pack(side="right")
        self.history_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=("Consolas", 10))
        self.history_text.pack(fill="both", expand=True)

    def _build_codes_tab(self):
        frame = ttk.Frame(self.tab_codes)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        top = ttk.Frame(frame)
        top.pack(fill="x", pady=(0, 8))
        ttk.Label(top, text="Search OBD2 codes:", font=("Segoe UI", 11, "bold")).pack(side="left")
        self.code_search = ttk.Entry(top, font=("Segoe UI", 12))
        self.code_search.pack(side="left", fill="x", expand=True, padx=(10, 10))
        self.code_search.bind("<KeyRelease>", lambda e: self._filter_codes())
        ttk.Button(top, text="Clear", command=lambda: (self.code_search.delete(0, tk.END), self._filter_codes())).pack(side="left")

        columns = ("code", "description", "severity", "cost", "diy")
        self.code_tree = ttk.Treeview(frame, columns=columns, show="headings", height=24)
        for col, heading in zip(columns, ["Code", "Description", "Severity", "Est. Cost", "DIY/Garage"]):
            self.code_tree.heading(col, text=heading)
            self.code_tree.column(col, width=90 if col == "code" else 180, anchor="w")
        self.code_tree.pack(fill="both", expand=True)
        self.code_tree.bind("<Double-1>", lambda e: self._open_code_from_tree())
        self._all_code_rows = []
        for code, data in OBD2_CODES.items():
            self._all_code_rows.append((code, data["description"], data["severity"], data["cost_estimate"], "DIY" if data.get("diy") else "Garage"))
        self._filter_codes()

    def _filter_codes(self):
        query = self.code_search.get().strip().lower()
        self.code_tree.delete(*self.code_tree.get_children())
        for row in self._all_code_rows:
            code, desc, sev, cost, diy = row
            if not query or query in code.lower() or query in desc.lower():
                self.code_tree.insert("", "end", values=(code, desc, sev, cost, diy))

    def _open_code_from_tree(self):
        item = self.code_tree.selection()
        if not item:
            return
        vals = self.code_tree.item(item[0], "values")
        code = vals[0]
        _, data = lookup_code(code)
        if not data:
            return
        win = tk.Toplevel(self.root)
        win.title(f"Code {code}")
        win.geometry("520x420")
        txt = scrolledtext.ScrolledText(win, wrap=tk.WORD, font=("Consolas", 10))
        txt.pack(fill="both", expand=True, padx=10, pady=10)
        txt.insert(tk.END, f"Code: {code}\n")
        txt.insert(tk.END, f"Description: {data['description']}\n")
        txt.insert(tk.END, f"Severity: {data['severity']} | Est. Cost: {data['cost_estimate']}\n")
        txt.insert(tk.END, f"Type: {'DIY possible' if data.get('diy') else 'Garage recommended'}\n\n")
        txt.insert(tk.END, "Symptoms: " + ", ".join(data["symptoms"]) + "\n")
        txt.insert(tk.END, "Causes: " + ", ".join(data["causes"]) + "\n")
        txt.insert(tk.END, "Repairs: " + "; ".join(data["repairs"]) + "\n")
        txt.config(state="disabled")

    def _build_obd2_tab(self):
        frame = ttk.Frame(self.tab_obd2)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        top = ttk.LabelFrame(frame, text="ELM327 / OBD2 Adapter")
        top.pack(fill="x", pady=(0, 10))

        row = ttk.Frame(top)
        row.pack(fill="x", padx=8, pady=6)
        ttk.Label(row, text="Port:").pack(side="left")
        self.obd_port = ttk.Entry(row, width=10)
        self.obd_port.insert(0, OBD2_PORT)
        self.obd_port.pack(side="left", padx=(8, 0))
        ttk.Label(row, text="Baud").pack(side="left", padx=(16, 0))
        self.obd_baud = ttk.Entry(row, width=10)
        self.obd_baud.insert(0, str(OBD2_BAUD))
        self.obd_baud.pack(side="left", padx=(8, 0))
        ttk.Button(row, text="Connect", command=self._connect_obd2).pack(side="left", padx=(16, 0))
        ttk.Button(row, text="Read Codes", command=self._read_live_codes).pack(side="left", padx=(8, 0))
        ttk.Button(row, text="Clear Codes", command=self._clear_obd2_codes).pack(side="left", padx=(8, 0))

        self.obd_status = ttk.Label(top, text="Status: not connected")
        self.obd_status.pack(anchor="w", padx=8, pady=(0, 8))

        self.obd_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=("Consolas", 10), height=22)
        self.obd_text.pack(fill="both", expand=True)

    def _connect_obd2(self):
        if not SERIAL_AVAILABLE:
            messagebox.showerror("Unavailable", "pyserial is not installed.")
            return
        port = self.obd_port.get().strip()
        baud = int(self.obd_baud.get().strip() or OBD2_BAUD)
        try:
            self.obd_serial = serial.Serial(port, baudrate=baud, timeout=1)
            self.obd_serial.write(b"ATZ\r")
            time.sleep(1)
            resp = self.obd_serial.read(self.obd_serial.in_waiting or 1).decode("utf-8", errors="ignore")
            self.obd_status.config(text=f"Status: connected on {port}")
            self.obd_text.insert(tk.END, f"Connected to {port} at {baud}\n{resp}\n")
        except Exception as e:
            self.obd_status.config(text="Status: connection failed")
            messagebox.showerror("OBD2 Error", str(e))

    def _read_live_codes(self):
        if not hasattr(self, "obd_serial") or not self.obd_serial or not self.obd_serial.is_open:
            messagebox.showwarning("Not connected", "Connect to an OBD2 adapter first.")
            return
        try:
            self.obd_serial.write(b"03\r")
            time.sleep(1)
            raw = self.obd_serial.read(self.obd_serial.in_waiting or 1).decode("utf-8", errors="ignore")
            self.obd_text.insert(tk.END, f"Raw response:\n{raw}\n")
            codes = re.findall(r"(P\d{4}|C\d{4}|B\d{4}|U\d{4})", raw.upper())
            if codes:
                self.obd_text.insert(tk.END, "Detected codes:\n")
                for code in codes:
                    _, data = lookup_code(code)
                    if data:
                        self.obd_text.insert(tk.END, f"{code}: {data['description']} | {data['cost_estimate']}\n")
                    else:
                        self.obd_text.insert(tk.END, f"{code}: unknown code\n")
            else:
                self.obd_text.insert(tk.END, "No codes detected.\n")
        except Exception as e:
            messagebox.showerror("Read failed", str(e))

    def _clear_obd2_codes(self):
        if not hasattr(self, "obd_serial") or not self.obd_serial or not self.obd_serial.is_open:
            messagebox.showwarning("Not connected", "Connect to an OBD2 adapter first.")
            return
        if not messagebox.askyesno("Confirm", "Clear all fault codes from the ECU?"):
            return
        try:
            self.obd_serial.write(b"04\r")
            time.sleep(1)
            raw = self.obd_serial.read(self.obd_serial.in_waiting or 1).decode("utf-8", errors="ignore")
            self.obd_text.insert(tk.END, f"Clear response:\n{raw}\n")
        except Exception as e:
            messagebox.showerror("Clear failed", str(e))

    def _build_service_tab(self):
        frame = ttk.Frame(self.tab_service)
        frame.pack(fill="both", expand=True, padx=12, pady=12)
        top = ttk.LabelFrame(frame, text="Add Service Record")
        top.pack(fill="x", pady=(0, 10))

        row1 = ttk.Frame(top)
        row1.pack(fill="x", padx=8, pady=6)
        ttk.Label(row1, text="Date (YYYY-MM-DD):").pack(side="left")
        self.svc_date = ttk.Entry(row1, width=14)
        self.svc_date.pack(side="left", padx=(8, 0))
        ttk.Label(row1, text="Mileage").pack(side="left", padx=(16, 0))
        self.svc_miles = ttk.Entry(row1, width=12)
        self.svc_miles.pack(side="left", padx=(8, 0))
        ttk.Label(row1, text="Item*").pack(side="left", padx=(16, 0))
        self.svc_item = ttk.Entry(row1, width=28)
        self.svc_item.pack(side="left", fill="x", expand=True, padx=(8, 0))

        row2 = ttk.Frame(top)
        row2.pack(fill="x", padx=8, pady=(0, 8))
        ttk.Label(row2, text="Garage").pack(side="left")
        self.svc_garage = ttk.Entry(row2, width=24)
        self.svc_garage.pack(side="left", padx=(8, 0))
        ttk.Label(row2, text="Cost").pack(side="left", padx=(16, 0))
        self.svc_cost = ttk.Entry(row2, width=12)
        self.svc_cost.pack(side="left", padx=(8, 0))
        ttk.Button(row2, text="Save", command=self._add_service).pack(side="left", padx=(16, 0))

        ttk.Label(frame, text="Service history:", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(6, 4))
        columns = ("id", "date", "mileage", "item", "garage", "cost", "notes")
        self.svc_tree = ttk.Treeview(frame, columns=columns, show="headings", height=18)
        for col, heading in zip(columns, ["#", "Date", "Miles", "Item", "Garage", "Cost", "Notes"]):
            self.svc_tree.heading(col, text=heading)
            self.svc_tree.column(col, width=70 if col == "id" else 140, anchor="w")
        self.svc_tree.pack(fill="both", expand=True)
        btns = ttk.Frame(frame)
        btns.pack(fill="x", pady=(8, 0))
        ttk.Button(btns, text="Delete Selected", command=self._delete_service).pack(side="left")
        ttk.Button(btns, text="Refresh", command=self._refresh_service).pack(side="left", padx=8)

    def _build_mot_tax_tab(self):
        frame = ttk.Frame(self.tab_mot_tax)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        top = ttk.LabelFrame(frame, text="Add MOT / Tax Reminder")
        top.pack(fill="x", pady=(0, 10))

        row = ttk.Frame(top)
        row.pack(fill="x", padx=8, pady=6)
        ttk.Label(row, text="Type").pack(side="left")
        self.mot_type = ttk.Combobox(row, values=["MOT", "Tax"], width=10, state="readonly")
        self.mot_type.pack(side="left", padx=(8, 0))
        self.mot_type.set("MOT")
        ttk.Label(row, text="Expiry (YYYY-MM-DD)").pack(side="left", padx=(16, 0))
        self.mot_expiry = ttk.Entry(row, width=14)
        self.mot_expiry.pack(side="left", padx=(8, 0))
        ttk.Button(row, text="Save", command=self._add_mot_tax).pack(side="left", padx=(16, 0))

        ttk.Label(frame, text="Saved reminders:", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(6, 4))
        columns = ("id", "type", "expiry", "status")
        self.mot_tree = ttk.Treeview(frame, columns=columns, show="headings", height=18)
        for col, heading in zip(columns, ["#", "Type", "Expiry", "Status"]):
            self.mot_tree.heading(col, text=heading)
            self.mot_tree.column(col, width=80 if col == "id" else 160, anchor="w")
        self.mot_tree.pack(fill="both", expand=True)
        btns = ttk.Frame(frame)
        btns.pack(fill="x", pady=(8, 0))
        ttk.Button(btns, text="Delete", command=self._delete_mot_tax).pack(side="left")
        ttk.Button(btns, text="Refresh", command=self._refresh_mot_tax).pack(side="left", padx=8)

    def _load_vehicle(self):
        for attr, key in [(self.veh_make, "make"), (self.veh_model, "model"), (self.veh_year, "year"),
                          (self.veh_engine, "engine"), (self.veh_mileage, "mileage"), (self.veh_vin, "vin")]:
            attr.delete(0, tk.END)
            attr.insert(0, self.config.get(key, ""))

    def _save_vehicle(self):
        self.config["make"] = self.veh_make.get().strip()
        self.config["model"] = self.veh_model.get().strip()
        self.config["year"] = self.veh_year.get().strip()
        self.config["engine"] = self.veh_engine.get().strip()
        self.config["mileage"] = self.veh_mileage.get().strip()
        self.config["vin"] = self.veh_vin.get().strip()
        save_config(self.config)

    def _sync_symptoms(self):
        self.selected_symptoms = [sym for sym, var in self.symptom_vars.items() if var.get()]

    def _vehicle_summary(self):
        parts = [f"{self.config.get('year','')} {self.config.get('make','')} {self.config.get('model','')}".strip(),
                 self.config.get("engine", ""),
                 f"{self.config.get('mileage','')} miles" if self.config.get("mileage") else ""]
        return " | ".join([p for p in parts if p])

    def _run_diagnosis(self):
        self._save_vehicle()
        custom = self.custom_symptom.get().strip()
        if custom:
            self.custom_symptom.delete(0, tk.END)
            match_text = custom
        elif self.selected_symptoms:
            match_text = " ".join(self.selected_symptoms)
        else:
            messagebox.showwarning("No symptoms", "Please pick symptoms or type a description.")
            return

        matches = diagnose_by_symptom(match_text)
        self.result_text.delete("1.0", tk.END)
        vehicle = self._vehicle_summary() or "Unknown vehicle"
        self.result_text.insert(tk.END, f"Vehicle: {vehicle}\n")
        self.result_text.insert(tk.END, f"Symptom(s): {custom or ', '.join(self.selected_symptoms)}\n\n")

        if not matches:
            self.result_text.insert(tk.END, "No strong matches found in the database.\n")
            self.result_text.insert(tk.END, "Next steps:\n")
            self.result_text.insert(tk.END, "  - Use an OBD2 scanner to read exact fault codes\n")
            self.result_text.insert(tk.END, "  - Check for loose connections or recent work\n")
            self.result_text.insert(tk.END, "  - Try broader symptoms like 'check engine light' or 'misfire'\n")
            log_diagnosis(vehicle=vehicle, symptom=custom or ", ".join(self.selected_symptoms), result="no_match")
            return

        self.result_text.insert(tk.END, f"Found {len(matches)} possible code(s), sorted by likelihood:\n\n")
        for code, data in matches.items():
            block = f"=== {code}: {data['description']} ===\n"
            block += f"Severity: {data['severity']} | Priority: {data.get('priority', '?')}\n"
            block += f"Est. Cost: {data['cost_estimate']} | {'DIY possible' if data.get('diy') else 'Garage recommended'}\n"
            block += "Symptoms: " + ", ".join(data["symptoms"]) + "\n"
            block += "Likely Causes: " + ", ".join(data["causes"]) + "\n"
            block += "Repairs: " + "; ".join(data["repairs"]) + "\n"
            block += "Next step: " + data["repairs"][0] + "\n\n"
            self.result_text.insert(tk.END, block)
        log_diagnosis(vehicle=vehicle, symptom=custom or ", ".join(self.selected_symptoms), result=f"matched: {', '.join(matches.keys())}")

    def _refresh_history(self):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT timestamp, vehicle, symptom, result, notes FROM diagnosis_log ORDER BY id DESC LIMIT 200")
        rows = cur.fetchall()
        conn.close()
        self.history_text.delete("1.0", tk.END)
        if not rows:
            self.history_text.insert(tk.END, "No history yet.\n")
        else:
            for ts, vehicle, symptom, result, notes in rows:
                line = f"[{ts}] {vehicle or 'Unknown vehicle'} | {symptom or 'N/A'} -> {result or 'N/A'}"
                if notes:
                    line += f" | {notes}"
                self.history_text.insert(tk.END, line + "\n")

    def _clear_history(self):
        if not messagebox.askyesno("Confirm", "Clear all diagnosis history?"):
            return
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("DELETE FROM diagnosis_log")
        conn.commit()
        conn.close()
        self._refresh_history()

    def _export_history(self):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT timestamp, vehicle, symptom, result, notes FROM diagnosis_log ORDER BY id ASC")
        rows = cur.fetchall()
        conn.close()
        if not rows:
            messagebox.showinfo("No history", "No history to export yet.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "vehicle", "symptom", "result", "notes"])
            for row in rows:
                writer.writerow(row)
        messagebox.showinfo("Exported", f"History exported to:\n{path}")

    def _print_report(self):
        content = self.result_text.get("1.0", tk.END).strip()
        if not content or "Vehicle:" not in content:
            messagebox.showinfo("Nothing to print", "Run a diagnosis first.")
            return
        tmp_path = Path(__file__).with_name("diagnosis_report.txt")
        tmp_path.write_text(content, encoding="utf-8")
        try:
            os.startfile(str(tmp_path), "print")
        except Exception as e:
            messagebox.showerror("Print failed", f"Could not print report.\n{e}")

    def _export_report(self):
        content = self.result_text.get("1.0", tk.END).strip()
        if not content or "Vehicle:" not in content:
            messagebox.showinfo("Nothing to export", "Run a diagnosis first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text", "*.txt"), ("CSV", "*.csv")])
        if not path:
            return
        if path.lower().endswith(".csv"):
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Field", "Value"])
                for line in content.splitlines():
                    writer.writerow(["", line])
        else:
            Path(path).write_text(content, encoding="utf-8")
        messagebox.showinfo("Exported", f"Report saved to:\n{path}")

    def _add_service(self):
        date = self.svc_date.get().strip()
        mileage = self.svc_miles.get().strip()
        item = self.svc_item.get().strip()
        garage = self.svc_garage.get().strip()
        cost = self.svc_cost.get().strip()
        if not date or not item:
            messagebox.showwarning("Input Required", "Date and item are required.")
            return
        try:
            datetime.date.fromisoformat(date)
        except ValueError:
            messagebox.showwarning("Invalid Date", "Use YYYY-MM-DD format.")
            return
        mileage_val = None
        if mileage:
            try:
                mileage_val = int(mileage)
            except ValueError:
                messagebox.showwarning("Invalid Mileage", "Mileage must be a number.")
                return
        cost_val = None
        if cost:
            try:
                cost_val = float(cost)
            except ValueError:
                messagebox.showwarning("Invalid Cost", "Cost must be a number.")
                return
        add_service(date, mileage_val, item, garage, cost_val)
        self.svc_date.delete(0, tk.END)
        self.svc_miles.delete(0, tk.END)
        self.svc_item.delete(0, tk.END)
        self.svc_garage.delete(0, tk.END)
        self.svc_cost.delete(0, tk.END)
        self._refresh_service()

    def _delete_service(self):
        item = self.svc_tree.selection()
        if not item:
            return
        if not messagebox.askyesno("Confirm", "Delete this service record?"):
            return
        vals = self.svc_tree.item(item[0], "values")
        delete_service(vals[0])
        self._refresh_service()

    def _refresh_service(self):
        rows = get_service_log()
        self.svc_tree.delete(*self.svc_tree.get_children())
        for r in rows:
            rid, date, mileage, item, garage, cost, notes = r
            self.svc_tree.insert("", "end", values=(rid, date, mileage or "", item, garage or "", cost or "", notes or ""))

    def _add_mot_tax(self):
        expiry_type = self.mot_type.get().strip()
        expiry_date = self.mot_expiry.get().strip()
        if not expiry_type or not expiry_date:
            messagebox.showwarning("Input Required", "Type and expiry date are required.")
            return
        try:
            datetime.date.fromisoformat(expiry_date)
        except ValueError:
            messagebox.showwarning("Invalid Date", "Use YYYY-MM-DD format.")
            return
        add_mot_tax(expiry_type, expiry_date)
        self.mot_expiry.delete(0, tk.END)
        self._refresh_mot_tax()

    def _delete_mot_tax(self):
        item = self.mot_tree.selection()
        if not item:
            return
        if not messagebox.askyesno("Confirm", "Delete this reminder?"):
            return
        vals = self.mot_tree.item(item[0], "values")
        delete_mot_tax(vals[0])
        self._refresh_mot_tax()

    def _refresh_mot_tax(self):
        rows = get_mot_tax()
        self.mot_tree.delete(*self.mot_tree.get_children())
        today = datetime.date.today().isoformat()
        for r in rows:
            rid, rtype, expiry, notified = r
            status = "OK"
            if expiry < today:
                status = "EXPIRED"
            elif (datetime.date.fromisoformat(expiry) - datetime.date.today()).days <= 30:
                status = "DUE SOON"
            self.mot_tree.insert("", "end", values=(rid, rtype, expiry, status))


def main():
    init_db()
    root = tk.Tk()
    app = CarDiagnosisApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
