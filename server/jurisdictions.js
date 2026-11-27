// Coverage: local governments whose agendas and legislation are published
// through the public Legistar Web API. Each `client` was verified to respond.
// Add a row to extend coverage; nothing else needs to change.
const j = (client, name, state, kind = 'city') => ({ client, name, state, kind });

export const JURISDICTIONS = [
  j('mesa', 'Mesa', 'AZ'), j('phoenix', 'Phoenix', 'AZ'), j('goodyear', 'Goodyear', 'AZ'), j('maricopa', 'Maricopa (city)', 'AZ'), j('pima', 'Pima County', 'AZ', 'county'),
  j('santaclara', 'Santa Clara', 'CA'), j('sanjose', 'San José', 'CA'), j('hayward', 'Hayward', 'CA'), j('oakland', 'Oakland', 'CA'), j('sacramento', 'Sacramento', 'CA'), j('dublin', 'Dublin', 'CA'),
  j('denver', 'Denver', 'CO'),
  j('fulton', 'Fulton County', 'GA', 'county'), j('dekalbcountyga', 'DeKalb County', 'GA', 'county'),
  j('naperville', 'Naperville', 'IL'), j('dupage', 'DuPage County', 'IL', 'county'),
  j('louisville', 'Louisville Metro', 'KY'),
  j('boston', 'Boston', 'MA'), j('baltimore', 'Baltimore', 'MD'), j('detroit', 'Detroit', 'MI'),
  j('stpaul', 'Saint Paul', 'MN'), j('dakota', 'Dakota County', 'MN', 'county'),
  j('kansascity', 'Kansas City', 'MO'),
  j('charlottenc', 'Charlotte', 'NC'), j('mecklenburg', 'Mecklenburg County', 'NC', 'county'), j('wake', 'Wake County', 'NC', 'county'),
  j('columbus', 'Columbus', 'OH'), j('toledo', 'Toledo', 'OH'),
  j('oklahomacounty', 'Oklahoma County', 'OK', 'county'),
  j('pittsburgh', 'Pittsburgh', 'PA'), j('nashville', 'Nashville', 'TN'),
  j('cityofdallas', 'Dallas', 'TX'), j('fortworthgov', 'Fort Worth', 'TX'), j('sanantonio', 'San Antonio', 'TX'), j('austintexas', 'Austin', 'TX'), j('elpasotexas', 'El Paso', 'TX'),
  j('pflugerville', 'Pflugerville', 'TX'), j('roundrock', 'Round Rock', 'TX'), j('grandprairie', 'Grand Prairie', 'TX'), j('mesquite', 'Mesquite', 'TX'), j('mckinney', 'McKinney', 'TX'), j('corpuschristi', 'Corpus Christi', 'TX'),
  j('slco', 'Salt Lake County', 'UT', 'county'),
  j('kingcounty', 'King County', 'WA', 'county'), j('seattle', 'Seattle', 'WA'), j('snohomish', 'Snohomish County', 'WA', 'county'),
  j('milwaukee', 'Milwaukee', 'WI'), j('madison', 'Madison', 'WI'), j('racine', 'Racine', 'WI'),
];

export const jurisdictionByClient = new Map(JURISDICTIONS.map((x) => [x.client, x]));
