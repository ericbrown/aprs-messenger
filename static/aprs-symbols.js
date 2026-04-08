// Complete APRS symbol table -> emoji mapping
// Primary table (symbol_table = '/') and Alternate table (symbol_table = '\')
// Reference: http://www.aprs.org/symbols/symbolsX.txt

const APRS_SYMBOLS = {
    // === Primary Table (/) ===
    '/!': '\u{1F6A8}', // Police station
    '/"': '\u{1F4E6}', // (reserved)
    '/#': '\u{1F4E1}', // Digi
    '/$': '\u{260E}',  // Phone
    '/%': '\u{1F4BB}', // DX Cluster
    '/&': '\u{1F310}', // HF Gateway
    "/\\'":'\u{2708}',  // Small aircraft (escaped single quote)
    '/(': '\u{1F4E1}', // Mobile Satellite Station
    '/)': '\u{267F}',  // Wheelchair/handicapped
    '/*': '\u{1F3CD}', // Snowmobile
    '/+': '\u{1F6D1}', // Red Cross
    '/,': '\u{269C}',  // Boy Scouts
    '/-': '\u{1F3E0}', // House QTH
    '/.': '\u{274C}',  // X / unknown position
    '//': '\u{1F534}', // Red dot
    '/0': '\u{0030}\u{FE0F}\u{20E3}', // Circle 0
    '/1': '\u{0031}\u{FE0F}\u{20E3}', // Circle 1
    '/2': '\u{0032}\u{FE0F}\u{20E3}', // Circle 2
    '/3': '\u{0033}\u{FE0F}\u{20E3}', // Circle 3
    '/4': '\u{0034}\u{FE0F}\u{20E3}', // Circle 4
    '/5': '\u{0035}\u{FE0F}\u{20E3}', // Circle 5
    '/6': '\u{0036}\u{FE0F}\u{20E3}', // Circle 6
    '/7': '\u{0037}\u{FE0F}\u{20E3}', // Circle 7
    '/8': '\u{0038}\u{FE0F}\u{20E3}', // Circle 8
    '/9': '\u{0039}\u{FE0F}\u{20E3}', // Circle 9
    '/:': '\u{1F525}', // Fire
    '/;': '\u{26FA}',  // Campground/portable
    '/<': '\u{1F3CD}', // Motorcycle
    '/=': '\u{1F682}', // Railroad engine
    '/>': '\u{1F697}', // Car
    '/?': '\u{1F5A5}', // File server
    '/@': '\u{1F300}', // Hurricane/tropical storm
    '/A': '\u{26D1}',  // Aid station
    '/B': '\u{1F4AC}', // BBS
    '/C': '\u{1F6F6}', // Canoe
    '/D': '\u{1F7E2}', // (reserved)
    '/E': '\u{1F441}', // Eyeball (event)
    '/F': '\u{1F69C}', // Farm vehicle/tractor
    '/G': '\u{1F5FA}', // Grid square (3x3)
    '/H': '\u{1F3E8}', // Hotel
    '/I': '\u{1F4E1}', // TCP/IP network station
    '/J': '\u{1F7E2}', // (reserved)
    '/K': '\u{1F3EB}', // School
    '/L': '\u{1F4BB}', // PC user (generic)
    '/M': '\u{1F34E}', // MacAPRS
    '/N': '\u{1F4F0}', // NTS station
    '/O': '\u{1F388}', // Balloon
    '/P': '\u{1F693}', // Police car
    '/Q': '\u{1F7E2}', // TBD
    '/R': '\u{1F699}', // Recreational vehicle
    '/S': '\u{1F680}', // Space shuttle
    '/T': '\u{1F4FA}', // SSTV
    '/U': '\u{1F68C}', // Bus
    '/V': '\u{1F4F9}', // ATV (amateur TV)
    '/W': '\u{1F327}', // National Weather Service
    '/X': '\u{1F681}', // Helicopter
    '/Y': '\u{26F5}',  // Sailboat/yacht
    '/Z': '\u{1F4BB}', // WinAPRS
    '/[': '\u{1F6B6}', // Jogger
    '/\\':'\u{1F53A}', // Triangle (DF)
    '/]': '\u{1F4EC}', // PBBS mailbox
    '/^': '\u{2708}\u{FE0F}',  // Large aircraft
    '/_': '\u{1F4A8}', // Weather station (WX)
    '/`': '\u{1F4E1}', // Dish antenna
    '/a': '\u{1F691}', // Ambulance
    '/b': '\u{1F6B2}', // Bicycle
    '/c': '\u{1F6A9}', // Incident Command Post
    '/d': '\u{1F692}', // Fire department
    '/e': '\u{1F40E}', // Horse/equestrian
    '/f': '\u{1F692}', // Fire truck
    '/g': '\u{1FA82}', // Glider
    '/h': '\u{1F3E5}', // Hospital
    '/i': '\u{1F3DD}', // IOTA (islands)
    '/j': '\u{1F699}', // Jeep
    '/k': '\u{1F69A}', // Truck
    '/l': '\u{1F4BB}', // Laptop
    '/m': '\u{1F4E1}', // Mic-E repeater
    '/n': '\u{1F4F6}', // Node (generic)
    '/o': '\u{1F3E2}', // Emergency operations center
    '/p': '\u{1F415}', // Dog
    '/q': '\u{1F5FA}', // Grid square (2x2)
    '/r': '\u{1F4E1}', // Repeater tower
    '/s': '\u{1F6A2}', // Ship (power boat)
    '/t': '\u{26FD}',  // Truck stop
    '/u': '\u{1F69B}', // 18-wheeler
    '/v': '\u{1F690}', // Van
    '/w': '\u{1F4A7}', // Water station
    '/x': '\u{1F4BB}', // xAPRS (Unix)
    '/y': '\u{1F3E0}', // House w/ yagi antenna
    '/z': '\u{1F7E2}', // (reserved)
    '/{': '\u{1F7E2}', // (reserved)
    '/|': '\u{1F7E2}', // TNC stream switch (reserved)
    '/}': '\u{1F7E2}', // (reserved)
    '/~': '\u{1F7E2}', // TNC stream switch (reserved)

    // === Alternate Table (\) ===
    '\\!': '\u{1F6A8}', // Emergency
    '\\"': '\u{1F7E2}', // (reserved)
    '\\#': '\u{1F4E1}', // Digi (alt overlay)
    '\\$': '\u{1F3E6}', // Bank/ATM
    '\\%': '\u{1F4BB}', // (reserved)
    '\\&': '\u{1F48E}', // Diamond (overlay)
    "\\\\'":'\u{1F6A8}', // Crash site
    '\\(': '\u{2601}',  // Cloudy
    '\\)': '\u{1F4E1}', // Firenet MEO
    '\\*': '\u{2744}',  // Snow
    '\\+': '\u{26EA}',  // Church
    '\\,': '\u{1F9D1}', // Girl Scouts
    '\\-': '\u{1F3E0}', // House (HF)
    '\\.': '\u{1F7E2}', // (reserved)
    '\\/': '\u{1F7E2}', // (reserved)
    '\\0': '\u{1F535}', // Circle (E-overlay)
    '\\1': '\u{1F535}', // (reserved)
    '\\2': '\u{1F535}', // (reserved)
    '\\3': '\u{1F535}', // (reserved)
    '\\4': '\u{1F535}', // (reserved)
    '\\5': '\u{1F535}', // (reserved)
    '\\6': '\u{1F535}', // (reserved)
    '\\7': '\u{1F535}', // (reserved)
    '\\8': '\u{1F535}', // (reserved)
    '\\9': '\u{26FD}',  // Gas station
    '\\:': '\u{1F525}', // Haze/fire
    '\\;': '\u{26FA}',  // Park/picnic
    '\\<': '\u{1F6A8}', // Advisory (single gale flag)
    '\\=': '\u{1F682}', // (reserved)
    '\\>': '\u{1F697}', // Car (alt)
    '\\?': '\u{2753}',  // Info kiosk
    '\\@': '\u{1F300}', // Hurricane/tropical storm
    '\\A': '\u{1F4E6}', // Box (overlay)
    '\\B': '\u{1F3D4}', // Blowing snow
    '\\C': '\u{1F6E5}', // Coast Guard
    '\\D': '\u{1F4A8}', // Drizzle
    '\\E': '\u{1F4A8}', // Smoke
    '\\F': '\u{1F976}', // Freezing rain
    '\\G': '\u{1F3D4}', // Snow shower
    '\\H': '\u{1F976}', // Haze
    '\\I': '\u{1F327}', // Rain shower
    '\\J': '\u{26A1}',  // Lightning
    '\\K': '\u{1F699}', // SUV/ATV
    '\\L': '\u{1F4BB}', // Laptop (alt)
    '\\M': '\u{1F4CD}', // Mic-E repeater (alt)
    '\\N': '\u{1F53A}', // Navigation buoy
    '\\O': '\u{1F6E9}', // Rocket
    '\\P': '\u{1F6BB}', // Parking/rest area
    '\\Q': '\u{1F327}', // Earthquake
    '\\R': '\u{1F4E1}', // Restaurant
    '\\S': '\u{1F4E1}', // Satellite/Pacsat
    '\\T': '\u{26C8}',  // Thunderstorm
    '\\U': '\u{2600}',  // Sunny
    '\\V': '\u{1F4E1}', // VORTAC nav aid
    '\\W': '\u{1F32A}', // NWS site (alt)
    '\\X': '\u{1F3E5}', // Pharmacy
    '\\Y': '\u{1F4E1}', // Radiosonde
    '\\Z': '\u{1F7E2}', // (reserved)
    '\\[': '\u{1F3C3}', // Wall cloud
    '\\\\':'\u{1F7E2}', // (reserved)
    '\\]': '\u{1F7E2}', // (reserved)
    '\\^': '\u{2708}\u{FE0F}', // Large aircraft (alt)
    '\\_': '\u{1F327}', // Weather station (alt WX)
    '\\`': '\u{1F327}', // Rain
    '\\a': '\u{1F48E}', // ARES/RACES
    '\\b': '\u{1F3D4}', // Blowing dust/sand
    '\\c': '\u{1F3E2}', // Civil Defense/RACES
    '\\d': '\u{1F4A8}', // DX spot
    '\\e': '\u{1F4A8}', // Sleet
    '\\f': '\u{1F32B}', // Funnel cloud
    '\\g': '\u{1F3D4}', // Gale flags
    '\\h': '\u{1F3EA}', // HAM store
    '\\i': '\u{1F4E6}', // Indoor/POI
    '\\j': '\u{1F6D1}', // Work zone/construction
    '\\k': '\u{1F699}', // SUV (special vehicle)
    '\\l': '\u{1F7E2}', // (reserved)
    '\\m': '\u{1F4CD}', // Milepost
    '\\n': '\u{1F6A9}', // Small triangle
    '\\o': '\u{1F7E2}', // (reserved)
    '\\p': '\u{1F7E2}', // (reserved)
    '\\q': '\u{1F7E2}', // (reserved)
    '\\r': '\u{1F4E1}', // Repeater (alt)
    '\\s': '\u{1F6A8}', // Sheriff/SAR
    '\\t': '\u{1F327}', // Tornado
    '\\u': '\u{1F69B}', // Truck (alt)
    '\\v': '\u{1F690}', // Van (alt)
    '\\w': '\u{1F32A}', // Flooding
    '\\x': '\u{1F7E2}', // (reserved)
    '\\y': '\u{1F7E2}', // (reserved)
    '\\z': '\u{1F7E2}', // (reserved)
    '\\{': '\u{1F32B}', // Fog
    '\\|': '\u{1F7E2}', // TNC stream switch (reserved)
    '\\}': '\u{1F7E2}', // (reserved)
    '\\~': '\u{1F7E2}', // TNC stream switch (reserved)
};

function symbolEmoji(sym) {
    if (!sym || sym.length < 2) return '\u{1F534}';  // red circle = no data
    return APRS_SYMBOLS[sym] || '\u{1F7E1}';  // yellow circle = unmapped
}
