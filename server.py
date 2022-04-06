#!/usr/bin/env python2.7
import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.debug=True

# Use the DB credentials you received by e-mail
DB_USER = "bh2798"
DB_PASSWORD = "2705"
DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"
DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/proj1part2"
engine = create_engine(DATABASEURI, isolation_level="AUTOCOMMIT")

##Insert Users
engine.execute("""DROP TABLE IF EXISTS Users CASCADE;""")
engine.execute("""CREATE TABLE Users(
email text,
name text,
gender text,
keyword int,
Primary key (email),
CHECK (gender='M' OR gender='F')
);""")
engine.execute("""INSERT INTO Users VALUES
('jackson@gmail.com', 'Jackson', 'M', 697010),
('andrew@gmail.com', 'Andrew', 'M', 115480),
('joshua@yahoo.com', 'Joshua', 'M', 147913),
('alex@gmail.com', 'Alex', 'M', 434119),
('eric@outlook.com', 'Eric', 'M', 362067),
('eva@gmail.com', 'Eva', 'F', 942887),
('julia@yahoo.com', 'Julia', 'F', 115626),
('abby@yahoo.com', 'Abby', 'F', 253862),
('cindy@gmail.com', 'Cindy', 'F', 470899),
('dora@gmail.com', 'Dora', 'F', 168569);""")

##Insert Movie
engine.execute("""DROP TABLE IF EXISTS Movie CASCADE;""")
engine.execute("""CREATE TABLE Movie(
idMovie int, 
title text UNIQUE NOT Null,
overview text,
release_date date,
Primary key (idMovie)
);""")
engine.execute("""
INSERT INTO Movie VALUES
(19995, 'Avatar', 
'In the 22nd century, a paraplegic Marine is dispatched to the moon Pandora on a unique mission, but becomes torn between following orders and protecting an alien civilization.',
'2009/12/10'),
(285, 'Pirates of the Caribbean: At World`s End',
'Captain Barbossa, long believed to be dead, has come back to life and is headed to the edge of the Earth with Will Turner and Elizabeth Swann. But nothing is quite as it seems.',
'2007-5-19'),
(206647, 'Spectre',
'A cryptic message from Bond past sends him on a trail to uncover a sinister organization. While M battles political forces to keep the secret service alive, Bond peels back the layers of deceit to reveal the terrible truth behind SPECTRE.',
'2015-10-26'),
(49026, 'The Dark Knight Rises',
'Following the death of District Attorney Harvey Dent, Batman assumes responsibility for Dent`s crimes to protect the late attorney`s reputation and is subsequently hunted by the Gotham City Police Department.',
'2012/7/16'),
(49529, 'John Carter',
'John Carter is a war-weary, former military captain who`s inexplicably transported to the mysterious and exotic planet of Barsoom (Mars) and reluctantly becomes embroiled in an epic conflict. It`s a world on the',
'2012/3/7'),
(559, 'Spider-Man 3',
'The seemingly invincible Spider-Man goes up against an all-new crop of villainincluding the shape-shifting Sandman. While Spider-Man superpowers are altered by an alien organism, his alter ego, Peter Parker, deals',
'2007/5/1'),
(38757, 'Tangled',
'When the kingdom`s most wanted-and most charming-bandit Flynn Rider hides out in a mysterious tower, he`s taken hostage by Rapunzel, a beautiful and feisty tower-bound teen with 70 feet of magical, golden hair. Flynn`s curious captor, who`s looking for her ticket out of the tower where she`s been locked away for years, strikes a deal with the handsome thief and the unlikely duo sets off on an action-packed escapade, complete with a super-cop horse, an over-protective chameleon and a gruff gang of pub thugs.',
'2010/11/24'),
(99861, 'Avengers: Age of Ultron',
'When Tony Stark tries to jumpstart a dormant peacekeeping program, things go awry and Earth Mightiest Heroes are put to the ultimate test as the fate of the planet hangs in the balance. As the villainous Ultron',
'2015/4/22'),
(767, 'Harry Potter and the Half-Blood Prince',
'As Harry begins his sixth year at Hogwarts, he discovers an old book marked as `Property of the Half-Blood Prince`, and begins to learn more about Lord Voldemort`s dark past.',
'2009/7/7'),
(209112, 'Batman v Superman: Dawn of Justice',
'Fearing the actions of a god-like Super Hero left unchecked, Gotham City own formidable, forceful vigilante takes on Metropolis most revered, modern-day savior, while the world wrestles with what sort of hero it really needs. And with Batman and Superman at war with one another, a new threat quickly arises, putting mankind in greater danger than it ever known before.',
'2016/3/23'),
(1452, 'Superman Returns',
'Superman returns to discover his 5-year absence has allowed Lex Luthor to walk free, and that those he was closest too felt abandoned and have moved on. Luthor plots his ultimate revenge that could see millions',
'2006/6/28'),
(10764, 'Quantum of Solace',
'Quantum of Solace continues the adventures of James Bond after Casino Royale. Betrayed by Vesper, the woman he loved, 007 fights the urge to make his latest mission personal. Pursuing his determination to',
'2008/10/30');""")

##Insert Comment
engine.execute("""DROP TABLE IF EXISTS Comment CASCADE;""")
engine.execute("""CREATE TABLE Comment(
comment_id int,
content text,
time date,
rating int,
email text,
idMovie int,
foreign key (email) references users(email) on delete no action,
foreign key (idMovie) references movie(idMovie) on delete no action,
Primary key (email,idMovie, comment_id),
CHECK (rating>=1 and rating<=10)
);""")
engine.execute("""INSERT INTO Comment VALUES
(1, 'How Can "Avatar" Have not Wined the Oscar of Best Film?', '2010/04/20', 10, 'jackson@gmail.com', 19995),
(2, 'Out there is the true world and here is the dream', '2009/12/19', 8, 'joshua@yahoo.com', 19995),
(3, 'Entertaining, But Too Long', '2007/12/09', 6, 'joshua@yahoo.com', 285),
(4, 'Complete overkill', '2012/06/22', 3, 'eva@gmail.com', 285),
(5, 'cool but not great', '2016/08/09', 7, 'abby@yahoo.com', 206647),
(6, 'The second weakest of the Craig Bonds', '2016/04/04', 5, 'alex@gmail.com', 206647),
(7, 'What a way to end the trilogy!', '2012/11/02', 9, 'eric@outlook.com', 49026),
(8, 'What a mess', '2021/07/19', 2, 'dora@gmail.com', 49529),
(9, 'Enjoyable, but the weakest of the series', '2010/01/16', 6, 'jackson@gmail.com', 559),
(10, 'Too many villains Too many story lines', '2014/02/22', 6, 'julia@yahoo.com', 559),
(11, 'A Delightful Animation Based on the Fairy Tale By The Grimm Brothers', '2011/06/18', 10, 'julia@yahoo.com', 38757),
(12, 'Not as good as the first film, still a solid sequel', '2016/06/06', 7, 'joshua@yahoo.com', 99861),
(13, 'EVERYONE CREATES THINGS THAT THEY DREAD', '2018/11/21', 9, 'andrew@gmail.com', 99861),
(14, 'Charming and Endearing!', '2001/11/28', 9, 'cindy@gmail.com', 767),
(15, 'Good Start to the Series', '2016/03/05', 10, 'eva@gmail.com', 767),
(16, 'Such potential, such a missed opportunity', '2016/05/29', 4, 'andrew@gmail.com', 209112),
(17, 'A hollow story presented in an explosion of special effects...', '2016/09/23', 6, 'alex@gmail.com', 209112),
(18, 'Superheroes Have Become Worse Than Villains', '2016/11/05', 5, 'dora@gmail.com', 209112),
(19, 'Clash of the Superheroes!' , '2016/04/08' , 9, 'eric@outlook.com', 209112),
(20, 'Thrilling and grandly entertaining adventure of the Man of Steel returning from Krypton', '2008/05/14', 6, 'julia@yahoo.com', 1452),
(21, 'a film that risks for greatness but does not fly high', '2006/06/27', 5, 'jackson@gmail.com', 1452),
(22, 'A good Way To Get a Headache', '2009/04/02', 1, 'cindy@gmail.com', 10764),
(23, 'Good But Should Have Been Better', '2008/11/02', 5, 'joshua@yahoo.com', 10764);""")

##Insert Actor
engine.execute("""DROP TABLE IF EXISTS Actor CASCADE;""")
engine.execute("""CREATE TABLE Actor(
actor_id int,
name text,
gender text,
Primary key (actor_id),
CHECK (gender='M' OR gender='F')
);""")
engine.execute("""INSERT INTO Actor VALUES
(64, 'Gary Oldman', 'M'),
(85, 'Johnny Depp', 'M'),
(116, 'Keira Knightly', 'F'),
(880, 'Ben Affleck', 'M'),
(2219, 'Tobey Maguire', 'M'),
(2517, 'Donna Murphy', 'M'),
(3223, 'Robert Downey Jr.', 'M'),
(3894, 'Christian Bale', 'M'),
(5309, 'Judi Dench', 'M'),
(5469, 'Ralph Fiennes', 'M'),
(7517, 'Kate Bosworth', 'F'),
(8691, 'Zoe Saldana', 'F'),
(8784, 'Daniel Craig', 'M'),
(10980, 'Daniel Redcliffe', 'M'),
(10989, 'Rupert Grint', 'M'),
(10990, 'Emma Watson', 'F'),
(16828, 'Chris Evans', 'M'),
(16855, 'Mandy Moore', 'M'),
(17052, 'Topher Grace', 'M'),
(17271, 'Brondon Routh', 'M'),
(19159, 'Thomas Haden Church', 'M'),
(28782, 'Monica Bellucci', 'F'),
(60900, 'Taylor Kitsch', 'M'),
(65731, 'Sam Worthington', 'M'),
(73968, 'Henry Cavill', 'F');""")

##Insert Characters
engine.execute("""DROP TABLE IF EXISTS Characters CASCADE;""")
engine.execute("""CREATE TABLE Characters(
character_id int,
name text,
idMovie int,
actor_id int,
foreign key (idMovie) references movie(idMovie) on delete no action,
foreign key (actor_id) references actor(actor_id) on delete no action,
Primary key (idMovie, actor_id, character_id)
);""")
engine.execute("""INSERT INTO Characters VALUES
(242, 'Jake Sully', 19995, 65731),
(3, 'Neytiri' ,19995, 8691),
(4, 'Captain Jack Sparrow', 285, 85),
(6, 'Elizabeth Swann', 285, 116),
(1, 'James Bond', 206647, 8784),
(10, 'M', 206647, 5469),
(17, 'Lucia', 206647, 28782),
(2, 'Bruce Wayne / Batman', 49026, 3894),
(5, 'James Gordon', 49026, 64),
(5, 'John Cater', 49529, 60900),
(30, 'Peter Parker / Spider-Man', 559, 2219),
(36, 'Flint Marko / Sandman', 559, 19159),
(37, 'Eddie Brock / Venom', 559, 17052),
(33, 'Rapunzel', 38757, 16855),
(35, 'Mother Gothel', 38757, 2517),
(76, 'Tony Stark / Iron Man', 99861, 3223),
(12, 'Steve Rogers / Captain America', 99861, 16828),
(3, 'Harry Potter', 767, 10980),
(2, 'Ron Weasley', 767, 10989),
(1, 'Hermione Grange', 767, 10990),
(18, 'Bruce Wayne / Batman', 209112, 880),
(14, 'Clark Tent / Superman', 209112, 73968),
(3, 'Clark Tent / Superman', 1452, 17271),
(4, 'Lois Lane', 1452, 7517),
(1, 'James Bond', 10764, 8784),
(19, 'M', 10764, 5309);""")

##insert Genre
engine.execute("""DROP TABLE IF EXISTS Genre CASCADE;""")
engine.execute("""CREATE TABLE Genre(
genre_id int,
name text,
Primary key (genre_id)
);""")
engine.execute("""INSERT INTO genre VALUES
(28, 'Action'),
(12, 'Advanture'),
(14, 'Fantasy'),
(878, 'Science Fiction'),
(80, 'Crime'),
(18, 'Drama'),
(53, 'Thriller'),
(16, 'Animation'),
(10751, 'Family'),
(37, 'Western'),
(35, 'Comedy'),
(10749, 'Romance');""")

##insert describe_genre
engine.execute("""DROP TABLE IF EXISTS describe_genre CASCADE;""")
engine.execute("""CREATE TABLE describe_genre(
genre_id int,
idMovie int,
foreign key (idMovie) references movie(idMovie) on delete no action,
foreign key (genre_id) references genre(genre_id) on delete no action,
primary key (idMovie,genre_id)
);""")
engine.execute("""INSERT INTO describe_genre VALUES
(12, 19995), (14, 19995), (28, 19995),
(12, 285), (14, 285), (28, 285),
(12, 206647), (28, 206647), (80, 206647),
(18, 49026), (28, 49026), (53, 49026), (80, 49026),
(12, 49529), (28, 49529), (878, 49529),
(12, 559), (14, 559), (28, 559),
(16, 38757), (10751, 38757),
(12, 99861), (28, 99861), (878, 99861),
(12, 767), (14, 767), (10751, 767),
(12, 209112), (14, 209112), (28, 209112),
(12, 1452), (14, 1452), (28, 1452), (878, 1452),
(12, 10764), (28, 10764), (53, 10764), (80, 10764);""")
##Insert Languages
engine.execute("""DROP TABLE IF EXISTS Languages CASCADE;""")
engine.execute("""CREATE TABLE languages(
language_id int,
name text,
primary key (language_id)
);""")
engine.execute("""INSERT INTO languages VALUES
(1, 'English'),
(2, 'Espanol'),
(3, 'Francais'),
(4, 'Italiano'),
(5, 'Deutsch'),
(6, 'Chinese'),
(7, 'Japanese'),
(8, 'Korean'),
(9, 'Russian'),
(10, 'Hebrew');""")
##Insert speak
engine.execute("""DROP TABLE IF EXISTS speak CASCADE;""")
engine.execute("""CREATE TABLE speak(
language_id int,
idMovie int,
foreign key (idMovie) references movie(idMovie) on delete no action,
foreign key (language_id) references languages(language_id) on delete no action,
primary key (idMovie, language_id)
);""")
engine.execute("""INSERT INTO speak VALUES
(1, 19995), (2, 19995),
(1, 285),
(1, 206647), (2, 206647), (3, 206647), (4, 206647), (5, 206647),
(1, 49026),
(1, 49529),
(1, 559), (3, 559),
(1, 38757),
(1, 99861), (6, 99861),
(1, 767),
(1, 209112),
(1, 1452), (3, 1452), (5, 1452),
(1, 10764), (2, 10764), (3, 10764), (4, 10764), (5, 10764);""")

##Insert Company
engine.execute("""DROP TABLE IF EXISTS Company CASCADE;""")
engine.execute("""CREATE TABLE Company(
Company_id int,
name text,
primary key (Company_id )
);""")
engine.execute("""INSERT INTO Company VALUES
(289,'Ingenious Film Partners'),
(306, 'Twentieth Century Fox Film Corporation'),
(444, 'Dune Entertainment'),
(574, 'Lightstorm Entertainment'),
(2, 'Walt Disney Pictures'),
(130, 'Jerry Bruckheimer Films'),
(19936, 'Second Mate Productions'),
(5, 'Columbia Pictures'),
(10761, 'Danjaq'),
(923, 'Legendary Picture'),
(6194, 'Warner Bros'),
(9993, 'DC Entertainment'),
(9996, 'Syncopy'),
(326, 'Laura Ziskin Productions'),
(19551, 'Marvel Enterprises'),
(6125, 'Walt Disney Animation Studios'),
(420, 'Marvel Studios'),
(15357, 'Prime Focus'),
(76043, 'Revolution Sun Studios'),
(7364, 'Heyday Films'),
(429, 'DC Comics'),
(507, 'Atlas Entertainment'),
(9168, 'Bad Hat Harry Productions'),
(7576, 'Eon Productions');""")

##Insert produce
engine.execute("""DROP TABLE IF EXISTS produce CASCADE;""")
engine.execute("""CREATE TABLE produce(
Company_id int,
idMovie int,
foreign key (idMovie) references movie(idMovie) on delete no action,
foreign key (Company_id) references Company(Company_id) on delete no action,
primary key (idMovie, Company_id)
);""")
engine.execute("""INSERT INTO produce VALUES
(289, 19995), (306, 19995), (444, 19995), (574, 19995),
(2, 285), (130, 285), (19936, 285),
(5, 206647), (10761, 206647),
(923, 49026), (6194, 49026), (9993, 49026), (9996, 49026),
(2, 49529),
(5, 559), (326, 559), (19551, 559),
(2, 38757), (6125, 38757),
(420, 99861), (15357, 99861), (76043, 99861),
(6194, 767), (7364, 767),
(429, 209112),(507, 209112), (9993, 209112),
(429, 1452), (923, 1452), (6194, 1452), (9168, 1452),
(7576, 10764);""")
##Insert Crew
engine.execute("""DROP TABLE IF EXISTS Crew CASCADE;""")
engine.execute("""CREATE TABLE Crew(
crew_id int NOT NULL,
name text,
gender text,
department text,
job text NOT NULL, 
primary key (crew_id, job),
CHECK (gender = 'M' OR gender='F')
);""")
engine.execute("""INSERT INTO Crew VALUES
(1721, 'Stephen E. Rivkin','M', 'Editing', 'Editor'),
(900, 'Christopher Boyes', 'M', 'Sound', 'Sound Designer'),
(900, 'Christopher Boyes', 'M', 'Sound', 'Supervising Sound Designer'),
(1704,  'Gore Verbinski', 'M', 'Directing', 'Director'),
(947, 'Hans Zimmer', 'M', ' Sound', 'Original Music Composer'),
(39, 'Sam Mendes', 'M', 'Directing', 'Director'),
(932, 'John Logan', 'M', 'Writing', 'Story'),
(1403411, 'Lucas Bielan', 'M', 'Camera', 'Camera Operator'),
(556, 'Emma Thomas' , 'F', 'Production', 'Producer'),
(1348686, 'Bradley Porter', 'M', 'Crew' , 'Production Office Assistant'),
(1355530, 'Cuitlahuac Morales Velazquez', 'M', 'Art', 'Sculptor'),
(7, 'Andrew Stanton', 'M', 'Writing', 'Screenplay'),
(7, 'Andrew Stanton', 'M', 'Directing', 'Director'),
(490, 'Colin Wilson', 'M', 'Production', 'Producer'),
(6958, 'Eric Zumbrunnen', 'M', 'Editing', 'Editor'),
(10570, 'Joseph M. Caracciolo Jr.', 'M', 'Production', 'Executive Producer'),
(7623, 'Sam Raimi', 'M', 'Writing', 'Screenplay'),
(7623, 'Sam Raimi', 'M', 'Directing', 'Director'),
(7624, 'Stan Lee', 'M', 'Writing', 'Author'),
(7879, 'John Lasseter', 'M', 'Production', 'Executive Producer'),
(5448, 'Wilhelm Grimm', 'M', 'Writing', 'Novel'),
(8020, 'John Kahrs', 'M', 'Visual Effects', 'Animation Supervisor'),
(531, 'Danny Elfman', 'M', 'Sound', 'Original Music Composer'),
(900, 'Christopher Boyes', 'M' ,'Sound', 'Sound Re-Recording Mixer'),
(7624, 'Stan Lee', 'M', 'Writing' ,'Characters'),
(10850, 'Kevin Feige', 'M', 'Production', 'Producer'),
(10966, 'J.K. Rowling', 'F', 'Writing', 'Novel'),
(10967, 'Steve Kloves', 'M', 'Writing', 'Screenplay'),
(10968, 'David Heyman', 'M', 'Production', 'Producer'),
(556, 'Emma Thomas' , 'F', 'Production', 'Executive Producer'),
(282, 'Charles Roven', 'M', 'Production', 'Producer'),
(9032, 'Bryan Singer', 'M', 'Directing', 'Director'),
(9032, 'Bryan Singer', 'M', 'Production', 'Producer'),
(9032, 'Bryan Singer', 'M',  'Writing', 'Story'),
(9039, 'John Ottman', 'M', 'Editing', 'Editor'),
(4248, 'Dennis Gassner', 'M', 'Art', 'Production Design'),
(9856, 'Ian Fleming', 'M', 'Writing', 'Characters'),
(4061, 'Louise Frogley', 'F', 'Custume & Make-Up', 'Custume Design');""")

##Insert work
engine.execute("""DROP TABLE IF EXISTS work CASCADE;""")
engine.execute("""CREATE TABLE work(
  crew_id INT NOT NULL,
  job text NOT NULL,
  idMovie INT NOT NULL,
  PRIMARY KEY (idMovie, crew_id, job),
  FOREIGN KEY (crew_id, job) REFERENCES Crew(crew_id, job) ON DELETE NO ACTION,
  FOREIGN KEY (idMovie) REFERENCES Movie(idMovie)
)""")
engine.execute("""INSERT INTO work VALUES
(1721, 'Editor', 19995), (900, 'Sound Designer', 19995), (900, 'Supervising Sound Designer', 19995),
(1721, 'Editor', 285), (1704, 'Director', 285), (947, 'Original Music Composer', 285),
(39, 'Director', 206647), (932, 'Story', 206647), (1403411, 'Camera Operator', 206647),
(947, 'Original Music Composer', 49026), (556, 'Producer', 49026), (1348686, 'Production Office Assistant', 49026),
(1355530, 'Sculptor', 49026),
(7, 'Director', 49529), (7, 'Screenplay', 49529), (490, 'Producer', 49529), (6958, 'Editor', 49529),
(10570, 'Executive Producer', 559), (7623, 'Screenplay', 559), (7623, 'Director', 559), (7624, 'Author', 559),
(7879, 'Executive Producer', 38757), (5448, 'Novel', 38757), (8020, 'Animation Supervisor', 38757),
(531, 'Original Music Composer', 99861), (900, 'Sound Re-Recording Mixer', 99861),
(7624, 'Characters', 99861), (10850, 'Producer', 99861),
(10966, 'Novel', 767), (10967, 'Screenplay', 767), (10968, 'Producer', 767),
(947, 'Original Music Composer', 209112), (556, 'Executive Producer', 209112), (282, 'Producer', 209112),
(9032, 'Producer', 1452), (9032, 'Director', 1452), (9032, 'Story', 1452), (9039, 'Editor', 1452),
(4248, 'Production Design', 10764), (9856, 'Characters', 10764), (4061, 'Custume Design', 10764);""")
##Insert follow
engine.execute("""DROP TABLE IF EXISTS follow CASCADE;""")
engine.execute("""CREATE TABLE follow(
email text,
actor_id int,
foreign key (email) references users(email) on delete no action,
foreign key (actor_id) references actor(actor_id) on delete no action,
primary key (email, actor_id)
);""")
engine.execute("""INSERT INTO follow VALUES
('jackson@gmail.com', 3223),
('jackson@gmail.com', 16828),
('joshua@yahoo.com', 8784),
('joshua@yahoo.com', 5469),
('abby@yahoo.com', 60900),
('eva@gmail.com', 10980),
('eva@gmail.com', 10989),
('eva@gmail.com', 10990),
('eric@outlook.com', 64),
('cindy@gmail.com', 2517),
('cindy@gmail.com', 85),
('andrew@gmail.com', 3223),
('joshua@yahoo.com', 3223),
('dora@gmail.com',10980),
('abby@yahoo.com', 7517),
('alex@gmail.com', 3894),
('jackson@gmail.com', 3894),
('alex@gmail.com', 3223),
('andrew@gmail.com', 19159),
('julia@yahoo.com', 2219);""")
##Insert like_list
engine.execute("""DROP TABLE IF EXISTS like_list CASCADE;""")
engine.execute("""CREATE TABLE like_list(
like_id SERIAL, 
email text,
name text, 
public int,
private int,
CHECK ((public =1 AND private=0) OR (public =0 AND private=1)),
foreign key (email) references users on DELETE CASCADE,
primary key (like_id, email, public, private)
);""")
engine.execute("""INSERT INTO like_list(name, email, public, private) VALUES
('Avatar', 'jackson@gmail.com',1 , 0),
('James Bond', 'joshua@yahoo.com',1 , 0),
('abby`s likelist', 'abby@yahoo.com',0, 1),
('Like', 'joshua@yahoo.com',1, 0),
('cindy','cindy@gmail.com',1, 0),
('dora likes','dora@gmail.com', 1, 0),
('Jackson','jackson@gmail.com',1,0 ),
('likelist','andrew@gmail.com',1,0 ),
('joshuas','joshua@yahoo.com',1,0 ),
('alexnet','alex@gmail.com',1,0 ),
('ericccc','eric@outlook.com',1,0 ),
('EVA','eva@gmail.com',1,0 ),
('julia s','julia@yahoo.com',1,0);""")
##insert include
engine.execute("""DROP TABLE IF EXISTS include CASCADE;""")
engine.execute("""CREATE TABLE include(
idMovie int,
like_id int,
email text,
public int, 
private int,
foreign key (like_id, email, public, private) references like_list(like_id, email, public, private),
foreign key (idMovie) references movie(idMovie) ON DELETE CASCADE,
primary key (like_id, idMovie)
);""")
engine.execute("""INSERT INTO include VALUES
(285, 1), (49529, 1), (559, 1), (559, 2), (99861, 2), (99861, 3), (767, 4), (49529, 4),
(559, 5), (38757, 5), (209112, 6), (10764, 6), (1452, 7), (767, 7), (99861, 7), (1452, 8),
(209112, 8), (209112, 9), (285, 9), (767, 10), (1452, 11), (99861, 12), (209112, 13);""")
##insert share
engine.execute("""DROP TABLE IF EXISTS share CASCADE;""")
engine.execute("""CREATE TABLE share(
like_id int,
public int,
private int,
email text not null, 
foreign key (like_id, email, public, private) references like_list(like_id, email, public, private),
CHECK (public=1 and private=0),
primary key (like_id,email)
);""")
engine.execute("""INSERT INTO share(email, like_id, public, private) VALUES
('jackson@gmail.com',1 ,1 , 0),
('joshua@yahoo.com',2 ,1 , 0),
('joshua@yahoo.com',4, 1, 0),
('cindy@gmail.com',5, 1, 0),
('dora@gmail.com', 6, 1, 0),
('jackson@gmail.com',7,1,0 ),
('andrew@gmail.com',8,1,0 ),
('joshua@yahoo.com',9,1,0 ),
('alex@gmail.com',10,1,0 ),
('eric@outlook.com',11,1,0 ),
('eva@gmail.com',12,1,0 );""")
@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass

@app.route('/')
def index():
  # DEBUG: this is debugging code to see what request looks like
  print(request.args)
  return render_template("index.html")


@app.route('/users/')
def user():
  names = []
  cursor=g.conn.execute(
                          """
                          SELECT Distinct Users.email, Users.name,  concat(Users.name, '''s like_list') as Users_likelist, concat(Users.name, '''s Actor_list') as Users_follow  FROM Users, like_list, comment, follow
                          Where Users.email=like_list.email and comment.email=Users.email and follow.email=Users.email
                          """)
  for result in cursor:
     names.append({'email':result['email'], 'name':result['name'], 'users_likelist':result['users_likelist'],
                   'users_follow':result['users_follow']})
  context = dict(data=names)
  cursor.close()
  return render_template("users.html", **context)

@app.route('/likelist/<name>/<str>',methods=['GET'])
def likelist(name, str):
  names=[]
  cursor=g.conn.execute("""
            SELECT U.name, L.name as like_list_name, L.like_id as id, M.title as Movie_title  FROM Users U
            JOIN like_list L on U.email=L.email
            JOIN include i on L.like_id=i.like_id 
            JOIN Movie M on i.idMovie=M.idMovie
            WHERE U.name=%s and L.public=1 and L.private=0
            GROUP BY U.name, L.name, L.like_id, M.title
            """, name)
  for result in cursor:
     names.append({'User_name':result['name'], 'like_list_name':result['like_list_name'],
                   'id':result['id'], 'users_follow':result['movie_title']})
  context = dict(data=names, name=name)
  cursor.close()
  return render_template("users_likelist.html", **context)

@app.route('/follow/<names>/<str1>',methods=['GET'])
def follow(names, str1):
  name=[]
  cursor=g.conn.execute("""
              Select U.name, A.name as actor FROM 
              Users U JOIN follow F on U.email=F.email
              JOIN actor A on F.actor_id=A.actor_id
              WHERE U.name=%s
                       """, names)
  for result in cursor:
     name.append({'User_name':result['name'], 'actor':result['actor']})
  context = dict(data=name, name=names)
  cursor.close()
  return render_template("users_follow.html", **context)


@app.route('/movie')
def movie():
  names=[]
  cursor=g.conn.execute("""
                SELECT title,	overview,	release_date FROM movie
                        """)
  for result in cursor:
     names.append({'title':result['title'], 'overview':result['overview'],
                   'release_date':result['release_date']})
  context = dict(data=names)
  cursor.close()
  return render_template("movies.html", **context)


@app.route('/profiles/<name>')
def profiles(name):
  names, titles=[],[]
  cursor=g.conn.execute("""
        SELECT M.title as title FROM movie M
        WHERE M.title=%s
          """, name)
  cursor_=g.conn.execute("""
                        SELECT M.title, C.rating, U.name as user, C.content as comment FROM movie M
                        JOIN comment C ON M.idmovie=C.idMovie 
                        JOIN Users U on U.email=C.email
                        WHERE M.title=%s
                        """, name
  )
  for result in cursor:
     titles.append({'title':result['title']})
  for result in cursor_:
     print(result)
     names.append({'title':result['title'], 'rating':result['rating'],
                   'user':result['user'], 'comment':result['comment']})
  context = dict(data=names, name=name, title=titles)
  cursor.close()
  return render_template("Movie_profiles.html",**context)


@app.route('/Languages/<name>')
def Languages(name):
  names=[]
  cursor=g.conn.execute("""
                SELECT L.name as languages  FROM Languages L
              JOIN speak S ON L.language_id=S.language_id
              JOIN Movie M on S.idmovie=M.idmovie
              WHERE M.title=%s
                        """, name)
  for result in cursor:
     names.append({'languages':result['languages']})
  context = dict(data=names, name=name)
  cursor.close()
  return render_template("Languages.html", **context)

@app.route('/Crew/<name>')
def Crew(name):
  names = []
  cursor = g.conn.execute("""
                      SELECT W.job as job, C.name as name  FROM crew C 
                      JOIN work W ON C.crew_id=W.crew_id
                      JOIN Movie M ON W.idmovie=M.idmovie
                      WHERE M.title=%s
                        """, name)
  for result in cursor:
    names.append({'job': result['job'], 'name': result['name']})
  context = dict(data=names, name=name)
  cursor.close()
  return render_template("Crew.html", **context)

@app.route('/Genres/<name>')
def Genres(name):
  names = []
  cursor = g.conn.execute("""
                        SELECT G.name as genre FROM describe_genre D
                        JOIN genre G on D.genre_id=G.genre_id 
                        JOIN movie M on D.idmovie=M.idmovie
                        WHERE M.title=%s
                        """, name)
  for result in cursor:
    names.append({'genre': result['genre']})
  context = dict(data=names, name=name)
  cursor.close()
  return render_template("Genres.html", **context)

@app.route('/Characters/<name>')
def Characters(name):
  names = []
  cursor = g.conn.execute("""
                        SELECT A.name as actor, C.name as character FROM Characters C
                        JOIN Movie M on C.idmovie=M.idMovie
                        JOIN Actor A on C.actor_id=A.actor_id
                        WHERE M.title=%s
                         """, name)
  for result in cursor:
    names.append({'actor': result['actor'], 'character':result['character']})
  context = dict(data=names, name=name)
  cursor.close()
  return render_template("Characters.html", **context)


@app.route('/Company/<name>')
def Company(name):
  names = []
  cursor = g.conn.execute("""
                      SELECT C.name as company FROM Movie M 
                      JOIN produce P on M.idmovie=P.idmovie
                      JOIN Company C on C.company_id=P.company_id 
                      WHERE M.title=%s
                         """, name)
  for result in cursor:
    names.append({'company': result['company']})
  context = dict(data=names, name=name)
  cursor.close()
  return render_template("Company.html", **context)

@app.route('/Actor/<name>')
def Actor(name):
  names = []
  cursor = g.conn.execute("""
                          SELECT A.name as actor, A.gender FROM Characters C
                          JOIN Movie M on C.idmovie=M.idMovie
                          JOIN Actor A on C.actor_id=A.actor_id
                          WHERE A.name=%s
                         """, name)
  for result in cursor:
    names.append({'actor': result['actor'], 'gender':result['gender']})
  context = dict(data=names, name=name)
  cursor.close()
  return render_template("Actors.html", **context)

@app.route('/followlist/<name>')
def followlist(name):
  names = []
  cursor = g.conn.execute("""
                          SELECT U.name as follower FROM follow F
                          JOIN Users U on F.email=U.email
                          JOIN Actor A on F.actor_id=A.actor_id
                          Where A.name=%s
                         """, name)
  for result in cursor:
    names.append({'follower':result['follower']})
  context = dict(data=names, name=name)
  cursor.close()
  return render_template("followlist.html", **context)

@app.route('/movielist/<name>')
def movielist(name):
  names = []
  cursor = g.conn.execute("""
                          SELECT A.name as actor, M.title as movie  FROM Characters C
                          JOIN Movie M on C.idmovie=M.idMovie
                          JOIN Actor A on C.actor_id=A.actor_id
                          WHERE A.name=%s
                         """, name)
  for result in cursor:
    names.append({'actor': result['actor'], 'movie':result['movie']})
  context = dict(data=names, name=name)
  cursor.close()
  return render_template("movielist.html", **context)

# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  print(name)
  cmd = 'INSERT INTO test(name) VALUES (:name1), (:name2)';
  g.conn.execute(text(cmd), name1 = name, name2 = name);
  return redirect('/')


@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8000, type=int)
  def run(debug, threaded, host, port):
    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)
  run()
