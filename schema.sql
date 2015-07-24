drop table if exists surveys;
create table surveys (
  id integer primary key autoincrement,
  title text not null,
  text text not null,
  is_open integer not null default 0,
  date_created datetime default current_timestamp,
  date_opened datetime default null,
  date_closed datetime default null
);

drop table if exists questions;
create table questions (
  id integer primary key autoincrement,
  surveys_id integer not null,
  text text not null,
  foreign key(surveys_id) references surveys(id)
);

drop table if exists options;
create table options (
  id integer primary key autoincrement,
  text text not null,
  questions_id integer not null,
  foreign key(questions_id) references questions(id)
);
  
drop table if exists responses;
create table responses (
  id integer primary key autoincrement,
  options_id integer not null,
  users_id integer not null,
  text text not null,
  date_created datetime default current_timestamp,
  foreign key(options_id) references options(id)
  foreign key(users_id) references users(id)
);

drop table if exists users;
create table users (
  id integer primary key autoincrement,
  email text not null,
  password text not null,
  name text,
  is_activated integer not null default 1,
  is_admin integer not null default 0,
  date_registered datetime default current_timestamp,
);
