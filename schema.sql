--DROP TABLE IF EXISTS Continents;
--DROP TABLE IF EXISTS Currency;
--DROP TABLE IF EXISTS Rates;

CREATE TABLE IF NOT EXISTS Continents (
	Id INTEGER PRIMARY KEY,
	Name TEXT DEFAULT "None"
);

CREATE TABLE IF NOT EXISTS Currencies (
	Id INTEGER PRIMARY KEY,
	Name TEXT,
	ContinentId INTEGER,
	FOREIGN KEY (ContinentId) REFERENCES Continents(Id)
);

CREATE TABLE IF NOT EXISTS Zones (
	Id INTEGER PRIMARY KEY,
	Name TEXT,
	ContinentId INTEGER,
	CurrencyId INTEGER,
	FOREIGN KEY (ContinentId) REFERENCES Continents(Id),
	FOREIGN KEY (CurrencyId) REFERENCES Currencies(Id)
);

CREATE TABLE IF NOT EXISTS Rates (
	Id INTEGER PRIMARY KEY,
	Name TEXT,
	Title TEXT,
	Href TEXT,
	ContinentId INTEGER,
	CurrencyId INTEGER,
	ZoneId INTEGER,
	FOREIGN KEY (ContinentId) REFERENCES Continents(Id),
	FOREIGN KEY (CurrencyId) REFERENCES Currencies(Id),
	FOREIGN KEY (ZoneId) REFERENCES Zone(Id)
);

