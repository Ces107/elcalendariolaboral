"""Appliance energy cost calculator (English twin of consumo-electrodomesticos): same compute, $ / £ / €."""
from herramientas.tools import _bricolaje as F
from herramientas.tools.consumo_electrodomesticos import JS, DOE, LABEL_EU_EN

PRESETS = [
    ("otro", "Other appliance"),
    ("fridge", "Refrigerator", {"w": "40", "h": "24"}), ("washer", "Washing machine (warm)", {"w": "900", "h": "1", "dias": "4"}),
    ("dish", "Dishwasher", {"w": "1200", "h": "1", "dias": "5"}), ("dryer", "Clothes dryer", {"w": "3000", "h": "1", "dias": "3"}),
    ("oven", "Electric oven", {"w": "2000", "h": "1", "dias": "3"}), ("micro", "Microwave", {"w": "1200", "h": "0.25"}),
    ("heater", "Space heater", {"w": "1500", "h": "4"}), ("window", "Window AC", {"w": "900", "h": "6"}),
    ("central", "Central AC", {"w": "3500", "h": "6"}), ("dehum", "Dehumidifier", {"w": "300", "h": "8"}),
    ("tv", "TV", {"w": "90", "h": "4"}), ("pc", "Desktop PC", {"w": "150", "h": "6"}), ("console", "Game console", {"w": "150", "h": "3"}),
    ("laptop", "Laptop", {"w": "45", "h": "6"}), ("router", "Wi-Fi router", {"w": "10", "h": "24"}),
    ("led", "LED bulb", {"w": "9", "h": "5"}), ("kettle", "Electric kettle", {"w": "2000", "h": "0.2"}),
]


def blocks(ctx):
    n = lambda x, d=0: F.n(x, d, True)  # noqa: E731
    heater = 1500 * 4 / 1000
    tv = 90 * 4 / 1000 * 365
    return [
        ("How much electricity does an appliance use", f"""
<p>Multiply the power in watts by the hours of use and divide by 1,000 to get kilowatt-hours; multiply by your price per kWh
to get the cost. A 1,500 W space heater running 4 hours a day uses {n(heater)} kWh a day; at 17 cents per kWh that is
${n(heater * 0.17, 2)} a day, about ${n(heater * 0.17 * 30, 0)} a month. A 90 W TV on for 4 hours a day uses {n(tv)} kWh a year,
around ${n(tv * 0.17, 0)}. This is the same method the US Department of Energy describes for estimating appliance use.</p>
<p>Anything with a thermostat or a compressor (fridges, freezers, ovens, water heaters, AC units) does not draw its full
rated power all the time. A fridge rated at 150 W averages 30 to 50 W over a day, which is why the preset uses 40 W for 24
hours. For those appliances the most accurate figure is on the label: the yellow EnergyGuide label in the US and the EU
energy label in Europe give the yearly kWh (and, in the EU, kWh per 100 cycles for washers and dishwashers).</p>"""),
        ("Which price to use", """
<p>Use the energy rate from your bill: the cents (or pence) per kWh charged for usage, including taxes and delivery charges if
they are billed per kWh. Fixed daily or monthly charges are paid whatever you use, so leave them out. If you are on a
time-of-use plan, run the calculation with the off-peak and peak rates to see what moving a load to the night saves. Choose
the currency with the button at the top; the calculator does not convert between currencies.</p>"""),
        ("Standby power", """
<p>Set-top boxes, sound bars, game consoles in rest mode and chargers left plugged in keep drawing power when "off". Add
standby watts under More options and the calculator counts them for every hour the device is not in use. Two or three watts
for a whole year add up to 18 to 26 kWh per device; a power strip with a switch removes it.</p>"""),
    ]


FAQ = [
    ("How much does it cost to run a 1,500 W heater?",
     "1.5 kWh per hour. At 17 cents per kWh that is about 26 cents an hour, $1.02 for four hours."),
    ("How do I convert watts to kWh?",
     "kWh = watts × hours ÷ 1,000. A 60 W bulb on for 10 hours uses 0.6 kWh."),
    ("How much electricity does a refrigerator use per year?",
     "A modern full-size fridge uses roughly 350 to 600 kWh a year in the US, less in smaller European models. The EnergyGuide label states it."),
    ("Where do I find an appliance's wattage?",
     "On the nameplate, usually on the back or bottom. If it shows amps, multiply by the voltage (120 V in the US, 230 V in Europe and the UK)."),
    ("Does unplugging appliances save money?",
     "Only for devices with real standby draw. Old electronics can draw 5 to 10 W around the clock; modern ones usually under 1 W."),
]

TOOL = {
    "slug": "appliance-energy-cost",
    "lang": "en",
    "twin": "consumo-electrodomesticos",
    "cat": F.CAT_EN[0], "cat_name": F.CAT_EN[1],
    "icon": "plug",
    "order": 65,
    "name": "Appliance energy cost",
    "k": "electricity cost calculator watts kwh per hour day month year appliance running cost standby",
    "title": "Appliance Energy Cost Calculator: kWh and Cost",
    "desc": "Work out how much electricity an appliance uses and what it costs per hour, day, month and year from its watts, hours and your rate.",
    "h1": "Appliance energy cost calculator",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "cur", "type": "seg", "label": "Currency", "value": "$", "options": [("$", "$"), ("£", "£"), ("€", "€")]},
        {"id": "ap", "type": "select", "label": "Appliance", "value": "heater", "options": PRESETS, "custom": "otro"},
        {"id": "w", "type": "number", "label": "Power", "value": "1500", "unit": "W"},
        {"id": "h", "type": "number", "label": "Hours/day", "value": "4", "unit": "h", "step": "0.05", "w": "s"},
        {"id": "dias", "type": "number", "label": "Days/week", "value": "7", "w": "s"},
        {"id": "precio", "type": "number", "label": "Rate", "value": "0.17", "unit": "per kWh", "step": "0.001", "w": "s"},
        {"id": "uds", "type": "number", "label": "Units", "value": "1", "w": "s", "more": True},
        {"id": "espera", "type": "number", "label": "Standby", "value": "0", "unit": "W", "w": "s", "more": True},
    ],
    "js": F.make(JS, True),
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("U.S. Department of Energy · Estimating appliance and home electronic energy use", DOE),
                ("Regulation (EU) 2017/1369 on energy labelling (EUR-Lex)", LABEL_EU_EN)],
    "related": ["paint-calculator", "concrete-calculator", "flooring-calculator", "tile-calculator"],
    "tests": [
        ({}, {"n.kwhDay": 6, "n.year": 372.3, "n.hour": 0.255}),
        ({"w": "60", "h": "10"}, {"n.kwhDay": 0.6}),
        ({"uds": "3", "w": "9", "h": "5"}, {"n.kwhYear": 49.28}),
        ({"w": "0"}, {"err": "Enter the power in watts."}),
    ],
}
