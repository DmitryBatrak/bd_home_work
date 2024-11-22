-- Задание 2
SELECT name_of_track AS "Назвние трека", duration AS "Продолжительность"
  FROM music_tracks
 GROUP BY  name_of_track, duration
 LIMIT 1;
 
SELECT name_of_track AS "Назвние трека"
  FROM music_tracks
 WHERE duration > 150;
 
SELECT collection_name AS "Название сборника"
  FROM collections
 WHERE year_of_issue BETWEEN 2018 AND 2020;
 
SELECT nickname AS "Исполнитель"
  FROM music_performers
 WHERE nickname NOT LIKE '% %';
 
SELECT name_of_track AS "Назвние трека"
  FROM music_tracks
 WHERE name_of_track ~* '\mmy\M'
 
 -- Задание3
SELECT genre_name AS "Жанр", COUNT(*) AS "Количество"
  FROM generes_of_music
  JOIN genre_and_performens ON generes_of_music.id = genre_and_performens.genre_names
 GROUP BY genre_name;
  
SELECT COUNT(*) AS "Количество"
  FROM list_of_albums
  JOIN music_tracks ON list_of_albums.album_name = music_tracks.albums_names
 WHERE year_of_issue BETWEEN 2019 AND 2020
 
SELECT albums_names AS "Название альбома", AVG(duration) AS "Средняя продолжительность"
  FROM music_tracks
 GROUP BY albums_names;

SELECT nickname AS "Исполнитель"
  FROM music_performers
 WHERE nickname NOT IN (
	SELECT nickname
	  FROM music_performers
      JOIN albums_and_performers ON music_performers.id = albums_and_performers.nick_name 
      JOIN list_of_albums ON albums_and_performers.albums_name = list_of_albums.id
     WHERE year_of_issue = 2020
);

SELECT collection_name AS "Сборник"
  FROM collections
  JOIN collections_and_tracks ON collections.id = collections_and_tracks.collection_names 
  JOIN music_tracks ON collections_and_tracks.name_of_tracks = music_tracks.id 
  JOIN list_of_albums ON music_tracks.albums_names = list_of_albums.album_name 
  JOIN albums_and_performers ON list_of_albums.id = albums_and_performers.albums_name
  JOIN music_performers ON albums_and_performers.nick_name = music_performers.id 
 WHERE nickname = 'Mac Miller';