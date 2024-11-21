CREATE TABLE IF NOT EXISTS generes_of_music (
	id SERIAL PRIMARY KEY, 
	genre_name VARCHAR(80) NOT NULL
);

CREATE TABLE IF NOT EXISTS music_performers (
	id SERIAL PRIMARY KEY,
	nickname VARCHAR(80) NOT NULL
);

CREATE TABLE IF NOT EXISTS genre_and_performens (
	genre_names INTEGER REFERENCES generes_of_music(id),
	nicknames INTEGER REFERENCES music_performers(id),
	CONSTRAINT pk PRIMARY KEY (genre_names, nicknames)
);

CREATE TABLE IF NOT EXISTS list_of_albums (
	id SERIAL PRIMARY KEY,
	year_of_issue INTEGER NOT NULL CHECK (year_of_issue > 1900),
	album_name VARCHAR(80) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS albums_and_performers (
	nick_name INTEGER REFERENCES music_performers(id),
	albums_name INTEGER REFERENCES list_of_albums(id),
	CONSTRAINT prk PRIMARY KEY (nick_name, albums_name)
);

CREATE TABLE IF NOT EXISTS music_tracks (
	id SERIAL PRIMARY KEY,
	albums_names TEXT REFERENCES list_of_albums(album_name),
	duration INTEGER NOT NULL CHECK (duration < 3600),
	name_of_track VARCHAR(80) NOT NULL
);

CREATE TABLE IF NOT EXISTS collections(
	id SERIAL PRIMARY KEY,
	year_of_issue INTEGER NOT NULL CHECK (year_of_issue > 1990),
	collection_name VARCHAR(80) NOT NULL
);

CREATE TABLE IF NOT EXISTS collections_and_tracks (
	name_of_tracks INTEGER REFERENCES music_tracks(id),
	collection_names INTEGER REFERENCES collections(id),
	CONSTRAINT prmk PRIMARY KEY (name_of_tracks, collection_names)
);
