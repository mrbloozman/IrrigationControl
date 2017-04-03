PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE tDay (
	pk_day integer primary key,
	label text);
INSERT INTO "tDay" VALUES(0,'Monday');
INSERT INTO "tDay" VALUES(1,'Tuesday');
INSERT INTO "tDay" VALUES(2,'Wednesday');
INSERT INTO "tDay" VALUES(3,'Thursday');
INSERT INTO "tDay" VALUES(4,'Friday');
INSERT INTO "tDay" VALUES(5,'Saturday');
INSERT INTO "tDay" VALUES(6,'Sunday');
CREATE TABLE tEvents (
	pk_id integer primary key autoincrement,
	timeStamp text,
	severity integer,
	message text
	);
CREATE TABLE tSeverity (
	severity integer primary key,
	label text);
INSERT INTO "tSeverity" VALUES(0,'INFO');
INSERT INTO "tSeverity" VALUES(1,'WARN');
INSERT INTO "tSeverity" VALUES(2,'ERROR');
CREATE TABLE tStatus (
pk_status integer primary key,
label text);
INSERT INTO "tStatus" VALUES(0,'off');
INSERT INTO "tStatus" VALUES(1,'on');
CREATE TABLE tSchedule (
pk_id integer primary key autoincrement,
zone integer,
day integer,
duration_minutes integer,
start_time text,
one_shot integer);
CREATE TABLE tBools (
pk_bool integer primary key,
bool_label text);
INSERT INTO "tBools" VALUES(0,'no');
INSERT INTO "tBools" VALUES(1,'yes');
CREATE TABLE tZone (
pk_zone text primary key,
label text,
status integer,
enabled integer);
DELETE FROM sqlite_sequence;
INSERT INTO "sqlite_sequence" VALUES('tEvents',3);
INSERT INTO "sqlite_sequence" VALUES('tSchedule',1);
CREATE VIEW vEvents as SELECT t1.pk_id, t1.timeStamp, t2.label as severity_label, t1.message FROM tEvents as t1 JOIN tSeverity as t2 ON t2.severity = t1.severity;
CREATE VIEW vZones as 
SELECT 
t1.pk_zone,
t1.label as zone_label,
t1.status,
t2.label as status_label,
t1.enabled,
t3.label as enabled_label
FROM tZone as t1, tStatus as t2, tStatus as t3
WHERE t2.pk_status = t1.status
AND t3.pk_status = t1.enabled;
CREATE VIEW vSchedules as 
SELECT t1.pk_id, 
t1.zone,
t2.label as zone_label,
t1.day,
t3.label as day_label,
t1.duration_minutes,
t1.start_time,
t4.bool_label as one_shot
FROM tSchedule as t1,
tZone as t2,
tDay as t3,
tBools as t4
WHERE t2.pk_zone = t1.zone
AND t3.pk_day = t1.day
AND t4.pk_bool = t1.one_shot;
COMMIT;
