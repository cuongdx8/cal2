create sequence connection_id_seq start 10000;

create table connection(
    id int primary key default nextval('connection_id_seq'),
    platform_id varchar,
    type varchar,
    username varchar,
    email varchar,
    credentials json,
    settings json,
    created_at timestamp,
    updated_at timestamp,
    sync_token varchar
);

alter sequence connection_id_seq owned by connection.id;


create table account_connection(
    account_id int,
    connection_id int,
    primary key (account_id, connection_id),
    foreign key (account_id) references  account(id),
    foreign key (connection_id) references  connection(id)
);

create sequence calendar_id_seq start 10000;

create table calendar(
    id int primary key default nextval('calendar_id_seq'),
    platform_id varchar,
    type varchar,
    description varchar,
    location varchar,
    summary varchar,
    timezone varchar,
    background_color varchar,
    color_id varchar,
    default_reminders json[],
    foreground_color varchar,
    notification_settings json,
    created_by json,
    created_at timestamp,
    updated_at timestamp
);

alter sequence calendar_id_seq owned by calendar.id;

create table connection_calendar(
    connection_id int,
    calendar_id int,
    access_role varchar,
    default_flag bool,
    primary key (connection_id, calendar_id),
    foreign key (connection_id) references connection(id),
    foreign key (calendar_id) references calendar(id)
);

create sequence event_id_seq start 10000;
create table event(
    id int primary key default nextval('event_id_seq'),
    calendar_id int,
    platform_id varchar,
    attachments json[],
    attendees json[],
    description varchar,
    color_id varchar,
    conference_data json,
    creator json,
    "end" json,
    end_time_unspecified bool,
    event_type varchar,
    extended_properties json,
    guests_can_invite_others bool,
    guests_can_modify bool,
    guests_can_see_other_guests bool,
    html_link varchar,
    uid varchar,
    location varchar,
    locked bool,
    organizer json,
    original_start_time json,
    private_copy bool,
    recurrence varchar[],
    recurring_event_id varchar,
    reminders json[],
    start json,
    status varchar,
    summary varchar,
    transparency varchar,
    updated timestamp,
    visibility varchar,
    foreign key (calendar_id) references calendar(id)
);
alter sequence event_id_seq owned by event.id;


create or replace procedure disconnect_connection(con_id int, acc_id int)
language plpgsql
as $$
declare
    count_result int;
begin
    count_result = (select count(account_id) count_result from account_connection where connection_id = con_id);
    raise notice 'Connection_id = %, Account_id = %, Count = %', con_id, acc_id, count_result;
    if count_result = 1 then
        raise notice 'remove all data relation to connection = %', con_id;
        create temp table temp_tabl_disconnect_connection as (select calendar_id from connection_calendar where calendar_id in ( select calendar_id from connection_calendar where connection_id = con_id ) group by calendar_id having count(calendar_id) = 1);
        delete from account_connection ac using connection con where ac.connection_id = con.id and con.id = con_id;
        delete from connection_calendar cc using connection con where cc.connection_id = con.id and con.id = con_id;
        delete from event using temp_tabl_disconnect_connection where event.calendar_id = temp_tabl_disconnect_connection.calendar_id;
        delete from calendar using temp_tabl_disconnect_connection where calendar.id = temp_tabl_disconnect_connection.calendar_id;
        delete from connection where id = con_id;
        drop table temp_tabl_disconnect_connection;
        raise notice 'remove all data relation to connection = % ----------End', con_id;
    end if;
    if count_result > 1 then
        raise notice 'remove record in account_connection';
        delete from account_connection where account_id = acc_id and connection_id = con_id;
    end if;

end;$$