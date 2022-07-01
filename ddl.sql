--
-- PostgreSQL database dump
--

-- Dumped from database version 13.5 (Ubuntu 13.5-0ubuntu0.21.04.1)
-- Dumped by pg_dump version 14.3

-- Started on 2022-07-01 15:30:23

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 229 (class 1255 OID 44059)
-- Name: disconnect_connection(integer, integer); Type: PROCEDURE; Schema: public; Owner: lcp39
--

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
        create temp table temp_tabl_calendar_disconnect_connection as (
            select calendar_id from connection_calendar
            where calendar_id in (
                select calendar_id from connection_calendar where connection_id = con_id
            )
            group by calendar_id having count(calendar_id) = 1
        );
        -- list event that have occur = 1 or occur > 2 and calendar owner is deleted

        create temp table temp_tabl_event_disconnect_connection as (
            select event_id, count(calendar_id) from (
                select ce.event_id event_id, ce.calendar_id, ce.owner_flag  from calendar_event ce join temp_tabl_calendar_disconnect_connection tmple on ce.calendar_id = tmple.calendar_id
            ) as ehrd
            group by ehrd.event_id having count(ehrd.calendar_id) = 1 or (count(ehrd.calendar_id) > 1 and bool_or(ehrd.owner_flag))
        );
        delete from account_connection ac using connection con where ac.connection_id = con.id and con.id = con_id;
        delete from connection_calendar cc using connection con where cc.connection_id = con.id and con.id = con_id;
        delete from calendar_event cc using temp_tabl_calendar_disconnect_connection tmpl where cc.calendar_id = tmpl.calendar_id;
        delete from event e using temp_tabl_event_disconnect_connection tmple where e.id = tmple.event_id;
        delete from calendar using temp_tabl_calendar_disconnect_connection where calendar.id = temp_tabl_calendar_disconnect_connection.calendar_id;
        delete from connection where id = con_id;

        -- Delete event where occur > 1 and all calendar is removed
        delete from event e using (
            select ce.event_id event_id from calendar_event  ce
            join temp_tabl_event_disconnect_connection tmpl
            on ce.event_id = tmpl.event_id
            group by ce.event_id having count(ce.event_id) = 0
        ) as orphan_event where e.id = orphan_event.event_id;
        drop table temp_tabl_calendar_disconnect_connection;
        drop table temp_tabl_event_disconnect_connection;
        raise notice 'remove all data relation to connection = % ----------End', con_id;
    end if;
    if count_result > 1 then
        raise notice 'remove record in account_connection';
        delete from account_connection where account_id = acc_id and connection_id = con_id;
    end if;

end;$$


ALTER PROCEDURE public.disconnect_connection(con_id integer, acc_id integer) OWNER TO lcp39;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 205 (class 1259 OID 35767)
-- Name: account; Type: TABLE; Schema: public; Owner: lcp39
--

CREATE TABLE public.account (
    id integer NOT NULL,
    platform_id character varying,
    type character varying,
    credentials json,
    username character varying,
    email character varying,
    password character varying,
    active_flag boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.account OWNER TO lcp39;

--
-- TOC entry 210 (class 1259 OID 43968)
-- Name: account_connection; Type: TABLE; Schema: public; Owner: lcp39
--

CREATE TABLE public.account_connection (
    account_id integer NOT NULL,
    connection_id integer NOT NULL
);


ALTER TABLE public.account_connection OWNER TO lcp39;

--
-- TOC entry 204 (class 1259 OID 35765)
-- Name: account_id_seq; Type: SEQUENCE; Schema: public; Owner: lcp39
--

CREATE SEQUENCE public.account_id_seq
    START WITH 10000
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.account_id_seq OWNER TO lcp39;

--
-- TOC entry 3078 (class 0 OID 0)
-- Dependencies: 204
-- Name: account_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lcp39
--

ALTER SEQUENCE public.account_id_seq OWNED BY public.account.id;


--
-- TOC entry 212 (class 1259 OID 43985)
-- Name: calendar; Type: TABLE; Schema: public; Owner: lcp39
--

CREATE TABLE public.calendar (
    id integer NOT NULL,
    platform_id character varying,
    type character varying,
    description character varying,
    location character varying,
    summary character varying,
    timezone character varying,
    background_color character varying,
    color_id character varying,
    default_reminders json[],
    foreground_color character varying,
    notification_settings json,
    created_by json,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.calendar OWNER TO lcp39;

--
-- TOC entry 216 (class 1259 OID 44095)
-- Name: calendar_event; Type: TABLE; Schema: public; Owner: lcp39
--

CREATE TABLE public.calendar_event (
    calendar_id integer NOT NULL,
    event_id integer NOT NULL,
    overrides json,
    owner_flag boolean,
    response_status character varying
);


ALTER TABLE public.calendar_event OWNER TO lcp39;

--
-- TOC entry 211 (class 1259 OID 43983)
-- Name: calendar_id_seq; Type: SEQUENCE; Schema: public; Owner: lcp39
--

CREATE SEQUENCE public.calendar_id_seq
    START WITH 10000
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.calendar_id_seq OWNER TO lcp39;

--
-- TOC entry 3079 (class 0 OID 0)
-- Dependencies: 211
-- Name: calendar_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lcp39
--

ALTER SEQUENCE public.calendar_id_seq OWNED BY public.calendar.id;


--
-- TOC entry 209 (class 1259 OID 43949)
-- Name: connection; Type: TABLE; Schema: public; Owner: lcp39
--

CREATE TABLE public.connection (
    id integer NOT NULL,
    platform_id character varying,
    type character varying,
    username character varying,
    email character varying,
    credentials json,
    settings json,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    sync_token character varying
);


ALTER TABLE public.connection OWNER TO lcp39;

--
-- TOC entry 213 (class 1259 OID 43994)
-- Name: connection_calendar; Type: TABLE; Schema: public; Owner: lcp39
--

CREATE TABLE public.connection_calendar (
    connection_id integer NOT NULL,
    calendar_id integer NOT NULL,
    access_role character varying,
    default_flag boolean
);


ALTER TABLE public.connection_calendar OWNER TO lcp39;

--
-- TOC entry 208 (class 1259 OID 43947)
-- Name: connection_id_seq; Type: SEQUENCE; Schema: public; Owner: lcp39
--

CREATE SEQUENCE public.connection_id_seq
    START WITH 10000
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.connection_id_seq OWNER TO lcp39;

--
-- TOC entry 3080 (class 0 OID 0)
-- Dependencies: 208
-- Name: connection_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lcp39
--

ALTER SEQUENCE public.connection_id_seq OWNED BY public.connection.id;


--
-- TOC entry 215 (class 1259 OID 44014)
-- Name: event; Type: TABLE; Schema: public; Owner: lcp39
--

CREATE TABLE public.event (
    id integer NOT NULL,
    platform_id character varying,
    attachments json[],
    attendees json[],
    description character varying,
    color_id character varying,
    conference_data json,
    creator json,
    "end" json,
    end_time_unspecified boolean,
    event_type character varying,
    extended_properties json,
    guests_can_invite_others boolean,
    guests_can_modify boolean,
    guests_can_see_other_guests boolean,
    html_link character varying,
    uid character varying,
    location character varying,
    locked boolean,
    organizer json,
    original_start_time json,
    private_copy boolean,
    recurrence character varying[],
    recurring_event_id character varying,
    reminders json[],
    start json,
    status character varying,
    summary character varying,
    transparency character varying,
    updated timestamp without time zone,
    visibility character varying
);


ALTER TABLE public.event OWNER TO lcp39;

--
-- TOC entry 214 (class 1259 OID 44012)
-- Name: event_id_seq; Type: SEQUENCE; Schema: public; Owner: lcp39
--

CREATE SEQUENCE public.event_id_seq
    START WITH 10000
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.event_id_seq OWNER TO lcp39;

--
-- TOC entry 3081 (class 0 OID 0)
-- Dependencies: 214
-- Name: event_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lcp39
--

ALTER SEQUENCE public.event_id_seq OWNED BY public.event.id;


--
-- TOC entry 207 (class 1259 OID 35778)
-- Name: profile; Type: TABLE; Schema: public; Owner: lcp39
--

CREATE TABLE public.profile (
    id integer NOT NULL,
    account_id integer,
    full_name character varying,
    avatar character varying,
    description character varying,
    language character varying,
    timezone character varying,
    time_format character varying,
    first_day_of_week character varying
);


ALTER TABLE public.profile OWNER TO lcp39;

--
-- TOC entry 206 (class 1259 OID 35776)
-- Name: profile_id_seq; Type: SEQUENCE; Schema: public; Owner: lcp39
--

CREATE SEQUENCE public.profile_id_seq
    START WITH 10000
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.profile_id_seq OWNER TO lcp39;

--
-- TOC entry 3082 (class 0 OID 0)
-- Dependencies: 206
-- Name: profile_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lcp39
--

ALTER SEQUENCE public.profile_id_seq OWNED BY public.profile.id;


--
-- TOC entry 2902 (class 2604 OID 35770)
-- Name: account id; Type: DEFAULT; Schema: public; Owner: lcp39
--

ALTER TABLE ONLY public.account ALTER COLUMN id SET DEFAULT nextval('public.account_id_seq'::regclass);


--
-- TOC entry 2905 (class 2604 OID 43988)
-- Name: calendar id; Type: DEFAULT; Schema: public; Owner: lcp39
--

ALTER TABLE ONLY public.calendar ALTER COLUMN id SET DEFAULT nextval('public.calendar_id_seq'::regclass);


--
-- TOC entry 2904 (class 2604 OID 43952)
-- Name: connection id; Type: DEFAULT; Schema: public; Owner: lcp39
--

ALTER TABLE ONLY public.connection ALTER COLUMN id SET DEFAULT nextval('public.connection_id_seq'::regclass);


--
-- TOC entry 2906 (class 2604 OID 44017)
-- Name: event id; Type: DEFAULT; Schema: public; Owner: lcp39
--

ALTER TABLE ONLY public.event ALTER COLUMN id SET DEFAULT nextval('public.event_id_seq'::regclass);


--
-- TOC entry 2903 (class 2604 OID 35781)
-- Name: profile id; Type: DEFAULT; Schema: public; Owner: lcp39
--

ALTER TABLE ONLY public.profile ALTER COLUMN id SET DEFAULT nextval('public.profile_id_seq'::regclass);


--
-- TOC entry 3061 (class 0 OID 35767)
-- Dependencies: 205
-- Data for Name: account; Type: TABLE DATA; Schema: public; Owner: lcp39
--

COPY public.account (id, platform_id, type, credentials, username, email, password, active_flag, created_at, updated_at) FROM stdin;
10005	3213112645627932	FACEBOOK	{"access_token": "EAANmYZC3wFTQBADh4N1LsISZANAfD5ETeDnZBkhsrRDRd6IX2sKuY2pZC5WtGyPgtnxgWeXXk3DwX7XXEtRvgNBij8QG5FvgpKjwzBeDEMVig16fPknzJ37Ug0u2zxyYd4yYXvKDijytQopUbvFgsjQkfoC1GR1JDcARyGydVZCijW9tsxSuxKHgUaO810PCVwMI036JOVHfDAgCtX9xcUtQa51pNhU4iAACai69r9DZCHESnr0EFA", "token_type": "bearer", "expires_in": 5116628}	\N	\N	\N	t	2022-06-30 03:27:10.231129	2022-06-30 03:27:10.231129
10003	\N	LOCAL\n	\N	doxuancuong96@gmail.com	doxuancuong96@gmail.com	$2b$12$GnnNYgJhvXzQv/pYW.0jEeHbpE3pV4ame1nk9OUHfbJk6I5ox747K	t	2022-06-27 09:33:44.518453	2022-06-28 04:41:06.068007
10006	105981503381327514283	GOOGLE	{"access_token": "ya29.A0ARrdaM8mAK35XSH0MAKSRq7EZsqX66YYmYcValIDT_a_o6-x1V_Q4sDjxMYNveSpPfdG497pJ4UkGMIRnf0uSGWkwxfFFWkMGmD7fIfrQFdgDTuz_2t4-T-9v95VW9vSENUoQiD8Xzx0YgKX1FenlYbCL_qMYUNnWUtBVEFTQVRBU0ZRRl91NjFWeWkyY0I1TTh2N1owTmd3MkVSN1I3dw0163", "expires_in": 3599, "refresh_token": "1//0eg9oTyJoY2I8CgYIARAAGA4SNwF-L9IrYY13RkUzO9NVrf4WpEXGEGaQY9HlAA3JOr7lXi-VpRbgMVJ5M86kyJnYryhOQN5oEFc", "scope": "https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/calendar.events openid https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/userinfo.profile", "token_type": "Bearer", "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjI2NTBhMmNlNDdiMWFiM2JhNDA5OTc5N2Y4YzA2ZWJjM2RlOTI4YWMiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhenAiOiI1NzQ4NjYwMjQ0NDQtNmhudGVrZHRzYzZzZWs5bzIycHVuNjA3MWU3dDRlaGYuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJhdWQiOiI1NzQ4NjYwMjQ0NDQtNmhudGVrZHRzYzZzZWs5bzIycHVuNjA3MWU3dDRlaGYuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMDU5ODE1MDMzODEzMjc1MTQyODMiLCJlbWFpbCI6ImRveHVhbmN1b25nMTk5NkBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiYXRfaGFzaCI6Im51MlZaMUpjZzlVTGxBUHYxejBEN3ciLCJuYW1lIjoiQ8awxqFuZyDEkOG7lyBYdcOibiIsInBpY3R1cmUiOiJodHRwczovL2xoMy5nb29nbGV1c2VyY29udGVudC5jb20vYS0vQU9oMTRHaEVTc05IRXF2STJwZ1VocVR1ZHFHRkNpN0V0cF93M25NOER4cVI9czk2LWMiLCJnaXZlbl9uYW1lIjoiQ8awxqFuZyIsImZhbWlseV9uYW1lIjoixJDhu5cgWHXDom4iLCJsb2NhbGUiOiJ2aSIsImlhdCI6MTY1NjU2MDIxNSwiZXhwIjoxNjU2NTYzODE1fQ.E1AAYAmhQ9tBB0fFbt9CzelDQAUp2PDxYh2On_eWmXCoUaGyzxKmb9lwaqUeZaYcWK6DbKJNyhz3sTOcH9LAlV2OE2sFiL-EbiOd8Tq68jBw7iz3Hr1ZXGI-_SPjIm3EawGjZOBNYmJu0LXh_gvm4VlssCcSzb-Ponju2XCIzba2dIdg_4GtqBoFKzslqgedgsMEHiZDWtDLvNVgN_RKq-RyH5VlutUJm0JBzCQ4tn1GyVeLE_-WEKNLLv23T8x0INW7yAznC-vyFNVGfcgxXFq9Cc8E2XDMS5cphiPqslfZAjoVeFe4ErUfPmVGzsQe0hQ3W-i86fyj45WrC8T4LQ"}	doxuancuong1996@gmail.com	doxuancuong1996@gmail.com	\N	t	2022-06-30 03:36:57.213384	2022-06-30 03:36:57.213384
10007	101094421688012606843	GOOGLE	{"access_token": "ya29.a0ARrdaM9sjk4BR-ku5tVlAsc0tqjlwywMTwSFKD_Zx31M5f6_-aCaHP25eDM-SEs8iFfyoRzx06TDru45KbqPdezbYYBrA4W73v7DQcx7W2Ke1x3LIEPmTHpSygwgV66N7slqkSqV7lS-p10acnomiJC4eLFt", "expires_in": 3599, "refresh_token": "1//0eCcum0fuPvYfCgYIARAAGA4SNwF-L9Ir8pg_Cf_wxaMLn3p8PMKjDkkNMB1iJ_TepIut7GuSfcfLnLt5pqlpqN17u4zxxAgXv6g", "scope": "https://www.googleapis.com/auth/userinfo.profile openid https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/calendar.events https://www.googleapis.com/auth/calendar", "token_type": "Bearer", "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjI2NTBhMmNlNDdiMWFiM2JhNDA5OTc5N2Y4YzA2ZWJjM2RlOTI4YWMiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhenAiOiI1NzQ4NjYwMjQ0NDQtNmhudGVrZHRzYzZzZWs5bzIycHVuNjA3MWU3dDRlaGYuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJhdWQiOiI1NzQ4NjYwMjQ0NDQtNmhudGVrZHRzYzZzZWs5bzIycHVuNjA3MWU3dDRlaGYuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMDEwOTQ0MjE2ODgwMTI2MDY4NDMiLCJlbWFpbCI6ImRveHVhbmN1b25nOTZAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImF0X2hhc2giOiJjejJTVW5ULVE5NzI1SHA5NE1UMGVnIiwibmFtZSI6IkPGsMahbmcgxJDhu5cgWHXDom4iLCJwaWN0dXJlIjoiaHR0cHM6Ly9saDMuZ29vZ2xldXNlcmNvbnRlbnQuY29tL2EtL0FPaDE0R2g1VmRHWkpidlQ5QTkzVTJ2Z1BWNnBBWUVTREV6VWQzY0dKMDJvTGc9czk2LWMiLCJnaXZlbl9uYW1lIjoiQ8awxqFuZyIsImZhbWlseV9uYW1lIjoixJDhu5cgWHXDom4iLCJsb2NhbGUiOiJlbiIsImlhdCI6MTY1NjU3MTI0NywiZXhwIjoxNjU2NTc0ODQ3fQ.qKF4vUCRaowdJX-rYC7YkCOLNGnPR2eBRKUHhmIw7T9YIHZhdiFWRJRCcpXqrgbH6kQ2xqkfUAge9HMJ7gOnsLRS_vUz47nfoNpsc38rQ-uW4YktCcvjOvnK22p3UK5NroPlnz3U5GPygQgVIZmTsdj37E9mXNbDAT5yucCAKv62DKJ9DUyMGZxunrLF4c2_7s_df8dWiA58vl3_Ge63--xIo9oQweOGlnJCeq4PSIVRTGXofuFmfCrXJMUZTrDff2oDU0vip9aTVLlGAHAqNDU9Tqh8M8_IosC6i95TIFETTwmPtqXLWCEalAXZpIQE6TFdaJp8VMjU4XXS-S_h_w"}	doxuancuong96@gmail.com	doxuancuong96@gmail.com	\N	t	2022-06-30 06:40:48.893523	2022-06-30 06:40:48.893523
\.


--
-- TOC entry 3066 (class 0 OID 43968)
-- Dependencies: 210
-- Data for Name: account_connection; Type: TABLE DATA; Schema: public; Owner: lcp39
--

COPY public.account_connection (account_id, connection_id) FROM stdin;
\.


--
-- TOC entry 3068 (class 0 OID 43985)
-- Dependencies: 212
-- Data for Name: calendar; Type: TABLE DATA; Schema: public; Owner: lcp39
--

COPY public.calendar (id, platform_id, type, description, location, summary, timezone, background_color, color_id, default_reminders, foreground_color, notification_settings, created_by, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 3072 (class 0 OID 44095)
-- Dependencies: 216
-- Data for Name: calendar_event; Type: TABLE DATA; Schema: public; Owner: lcp39
--

COPY public.calendar_event (calendar_id, event_id, overrides, owner_flag, response_status) FROM stdin;
\.


--
-- TOC entry 3065 (class 0 OID 43949)
-- Dependencies: 209
-- Data for Name: connection; Type: TABLE DATA; Schema: public; Owner: lcp39
--

COPY public.connection (id, platform_id, type, username, email, credentials, settings, created_at, updated_at, sync_token) FROM stdin;
\.


--
-- TOC entry 3069 (class 0 OID 43994)
-- Dependencies: 213
-- Data for Name: connection_calendar; Type: TABLE DATA; Schema: public; Owner: lcp39
--

COPY public.connection_calendar (connection_id, calendar_id, access_role, default_flag) FROM stdin;
\.


--
-- TOC entry 3071 (class 0 OID 44014)
-- Dependencies: 215
-- Data for Name: event; Type: TABLE DATA; Schema: public; Owner: lcp39
--

COPY public.event (id, platform_id, attachments, attendees, description, color_id, conference_data, creator, "end", end_time_unspecified, event_type, extended_properties, guests_can_invite_others, guests_can_modify, guests_can_see_other_guests, html_link, uid, location, locked, organizer, original_start_time, private_copy, recurrence, recurring_event_id, reminders, start, status, summary, transparency, updated, visibility) FROM stdin;
10298	5ae1515p8115ie0kk121aeghpl	\N	\N	\N	\N	null	{"email": "doxuancuong96@gmail.com"}	{"dateTime": "2022-06-15T07:30:00Z", "timeZone": "Atlantic/Azores"}	\N	default	null	\N	\N	\N	https://www.google.com/calendar/event?eid=NWFlMTUxNXA4MTE1aWUwa2sxMjFhZWdocGwgdmhuY3F2ZDg4bmtxcjdlZWdkb201bDExZXNAZw	5ae1515p8115ie0kk121aeghpl@google.com	\N	\N	{"email": "vhncqvd88nkqr7eegdom5l11es@group.calendar.google.com", "displayName": "abc", "self": true}	null	\N	\N	\N	{"\\"useDefault\\""}	{"dateTime": "2022-06-15T06:30:00Z", "timeZone": "Atlantic/Azores"}	confirmed	aasdfs	\N	2022-06-15 03:19:31.766	\N
10299	bs7ip2mrnnbh4tmdpvev37lfk0	\N	\N	\N	\N	null	{"email": "doxuancuong96@gmail.com"}	{"dateTime": "2022-06-23T08:21:29Z", "timeZone": "Atlantic/Azores"}	\N	default	null	\N	\N	\N	https://www.google.com/calendar/event?eid=YnM3aXAybXJubmJoNHRtZHB2ZXYzN2xmazBfMjAyMjA2MjNUMDQ0MTI5WiBpaDRuZ2g2dm1wMGhlbHBtNGo4NTdpcG9iNEBn	bs7ip2mrnnbh4tmdpvev37lfk0@google.com	hanoi	\N	{"email": "ih4ngh6vmp0helpm4j857ipob4@group.calendar.google.com", "displayName": "t\\u00e9t", "self": true}	null	\N	{RRULE:FREQ=DAILY;UNTIL=20220623T235959Z}	\N	{"\\"useDefault\\"","\\"overrides\\""}	{"dateTime": "2022-06-23T04:41:29Z", "timeZone": "Atlantic/Azores"}	confirmed	Day la tieu de 8	\N	2022-06-24 04:16:21.052	\N
10300	6u6t42bqsbgg4tp4spl4c5k7do	\N	\N	\N	\N	null	{"email": "doxuancuong96@gmail.com"}	{"dateTime": "2022-06-23T08:21:29Z", "timeZone": "Atlantic/Azores"}	\N	default	null	\N	\N	\N	https://www.google.com/calendar/event?eid=NnU2dDQyYnFzYmdnNHRwNHNwbDRjNWs3ZG9fMjAyMjA2MjNUMDQ0NTI5WiBpaDRuZ2g2dm1wMGhlbHBtNGo4NTdpcG9iNEBn	6u6t42bqsbgg4tp4spl4c5k7do@google.com	hanoi	\N	{"email": "ih4ngh6vmp0helpm4j857ipob4@group.calendar.google.com", "displayName": "t\\u00e9t", "self": true}	null	\N	{RRULE:FREQ=DAILY;UNTIL=20220623T235959Z}	\N	{"\\"useDefault\\"","\\"overrides\\""}	{"dateTime": "2022-06-23T04:45:29Z", "timeZone": "Atlantic/Azores"}	confirmed	Day la tieu de 8	\N	2022-06-24 04:16:26.28	\N
10301	1cv3n8b9fovd1qifi9bm6tr748	\N	\N	\N	\N	null	{"email": "doxuancuong96@gmail.com"}	{"dateTime": "2022-06-23T08:21:29Z", "timeZone": "Atlantic/Azores"}	\N	default	null	\N	\N	\N	https://www.google.com/calendar/event?eid=MWN2M244Yjlmb3ZkMXFpZmk5Ym02dHI3NDhfMjAyMjA2MjNUMDMzNzI5WiBpaDRuZ2g2dm1wMGhlbHBtNGo4NTdpcG9iNEBn	1cv3n8b9fovd1qifi9bm6tr748@google.com	hanoi	\N	{"email": "ih4ngh6vmp0helpm4j857ipob4@group.calendar.google.com", "displayName": "t\\u00e9t", "self": true}	null	\N	{RRULE:FREQ=DAILY;UNTIL=20220623T235959Z}	\N	{"\\"useDefault\\"","\\"overrides\\""}	{"dateTime": "2022-06-23T03:37:29Z", "timeZone": "Atlantic/Azores"}	confirmed	Day la tieu de 7	\N	2022-06-24 04:16:30.806	\N
10302	eduqo4vhu64njtgc98he7244rk	\N	\N	\N	\N	null	{"email": "doxuancuong96@gmail.com"}	{"dateTime": "2022-06-23T08:21:29Z", "timeZone": "Atlantic/Azores"}	\N	default	null	\N	\N	\N	https://www.google.com/calendar/event?eid=ZWR1cW80dmh1NjRuanRnYzk4aGU3MjQ0cmtfMjAyMjA2MjNUMDQ1MDI5WiBpaDRuZ2g2dm1wMGhlbHBtNGo4NTdpcG9iNEBn	eduqo4vhu64njtgc98he7244rk@google.com	hanoi	\N	{"email": "ih4ngh6vmp0helpm4j857ipob4@group.calendar.google.com", "displayName": "t\\u00e9t", "self": true}	null	\N	{RRULE:FREQ=DAILY;UNTIL=20220623T235959Z}	\N	{"\\"useDefault\\"","\\"overrides\\""}	{"dateTime": "2022-06-23T04:50:29Z", "timeZone": "Atlantic/Azores"}	confirmed	Day la tieu de 8	\N	2022-06-24 04:22:46.91	\N
10303	ncfrnhhqif8ig5omdc68b48ppo	\N	\N	\N	\N	null	{"email": "doxuancuong96@gmail.com"}	{"dateTime": "2022-06-23T08:21:29Z", "timeZone": "Atlantic/Azores"}	\N	default	null	\N	\N	\N	https://www.google.com/calendar/event?eid=bmNmcm5oaHFpZjhpZzVvbWRjNjhiNDhwcG9fMjAyMjA2MjNUMDUxMDI5WiBpaDRuZ2g2dm1wMGhlbHBtNGo4NTdpcG9iNEBn	ncfrnhhqif8ig5omdc68b48ppo@google.com	hanoi	\N	{"email": "ih4ngh6vmp0helpm4j857ipob4@group.calendar.google.com", "displayName": "t\\u00e9t", "self": true}	null	\N	{RRULE:FREQ=DAILY}	\N	{"\\"useDefault\\"","\\"overrides\\""}	{"dateTime": "2022-06-23T05:10:29Z", "timeZone": "Atlantic/Azores"}	confirmed	Day la tieu de 8	\N	2022-06-24 04:38:32.674	\N
10304	l40jbnv5ls57sa3hqump3h94a0	\N	\N	\N	\N	null	{"email": "doxuancuong96@gmail.com"}	{"dateTime": "2022-06-23T08:21:29Z", "timeZone": "Atlantic/Azores"}	\N	default	null	\N	\N	\N	https://www.google.com/calendar/event?eid=bDQwamJudjVsczU3c2EzaHF1bXAzaDk0YTBfMjAyMjA2MjNUMDUxMzI5WiBpaDRuZ2g2dm1wMGhlbHBtNGo4NTdpcG9iNEBn	l40jbnv5ls57sa3hqump3h94a0@google.com	hanoi	\N	{"email": "ih4ngh6vmp0helpm4j857ipob4@group.calendar.google.com", "displayName": "t\\u00e9t", "self": true}	null	\N	{RRULE:FREQ=DAILY}	\N	{"\\"useDefault\\"","\\"overrides\\""}	{"dateTime": "2022-06-23T05:13:29Z", "timeZone": "Atlantic/Azores"}	confirmed	Day la tieu de 8	\N	2022-06-24 04:43:07.064	\N
10305	l845bjta0jajbq1fi7nqbpck7g	\N	\N	\N	\N	null	{"email": "doxuancuong96@gmail.com"}	{"dateTime": "2022-06-23T08:21:29Z", "timeZone": "Atlantic/Azores"}	\N	default	null	\N	\N	\N	https://www.google.com/calendar/event?eid=bDg0NWJqdGEwamFqYnExZmk3bnFicGNrN2dfMjAyMjA2MjNUMDUxNTI5WiBpaDRuZ2g2dm1wMGhlbHBtNGo4NTdpcG9iNEBn	l845bjta0jajbq1fi7nqbpck7g@google.com	hanoi	\N	{"email": "ih4ngh6vmp0helpm4j857ipob4@group.calendar.google.com", "displayName": "t\\u00e9t", "self": true}	null	\N	{RRULE:FREQ=DAILY}	\N	{"\\"useDefault\\"","\\"overrides\\""}	{"dateTime": "2022-06-23T05:15:29Z", "timeZone": "Atlantic/Azores"}	confirmed	Day la tieu de 8	\N	2022-06-24 04:44:41.942	\N
10314	50o9qjejo7vdsghv1ksa1h1pho	\N	\N	<p>Xin chào Anh/Chị</p><p>Email này thay cho lời chào mừng của chương trình Bệ phóng Việt Nam Digital 4.0 dành cho anh/chị khi tham gia lớp học:</p><p></p><ul><li>Địa chỉ Liên kết của Lớp học:&nbsp;<a href="https://youtu.be/ofGITKLT3aQ" id="ow637" __is_owner="true">https://youtu.be/ofGITKLT3aQ</a></li><li>Thông tin lớp học: [8/11] Chủ nhật - 10:30 - 11:30 - I11&nbsp;- Giữ an toàn cho bản thân trong thế giới số</li></ul>Lưu ý:<p></p><p></p><ul><li>Liên kết tham dự bắt đầu hoạt động vào ngày giờ tương ứng củalớp học.</li><li>Anh/Chị vui lòng điền Feedback Form cuối buổi học để được nhận chứng chỉ từ chương trình nhé.</li><li>Liên kết tham dự trên chỉ dành riêng cho các học viên đã đăng ký Tham dự đào tạo Trực tuyến ở Thư mời, vui lòng không chia sẻ công khai trên nhằm đảm bảo tính công bằng và bảo mật.</li></ul><br><p></p><table><tbody><tr><td>Để buổi đào tạo diễn ra thành công, vui lòng tham khảo cách tham gia qua&nbsp;<a href="https://docs.google.com/document/d/1eLkoVO3QR6QDG796k_eQzhu6nj8vjDatk9qQXZIbcFg/edit?usp=sharing">“Hướng dẫn xem livestream trên YouTube”</a></td></tr></tbody></table><p>Nếu có bất kỳ thắc mắc nào về chương trình, anh/chị có thể liên hệ số Hotline: 028.7770.7787 để đặt câu hỏi trực tiếp cho chương trình hoặc tương tác bằng cách đặt câu hỏi trên nền tảng YouTube khi tham gia xem YouTubeLivestream.</p><p>Chúc anh/chị có nhiều sức khỏe, anh/chị nhớ tham gia học đúng giờ và theo dõi kênh YouTube&nbsp;<a href="https://www.youtube.com/channel/UCWVMQ6Cxim1eCFIeSXajj9g/channels">Bệ phóng Việt Nam Digital 4.0</a>&nbsp;của lớp nhé!</p>	\N	null	{"email": "hanoiadmin@rsvp.com.vn"}	{"dateTime": "2020-11-08T03:30:00-01:00"}	\N	default	null	\N	\N	f	https://www.google.com/calendar/event?eid=NTBvOXFqZWpvN3Zkc2dodjFrc2ExaDFwaG8gZG94dWFuY3Vvbmc5NkBt	50o9qjejo7vdsghv1ksa1h1pho@google.com	\N	\N	{"email": "hanoiadmin@rsvp.com.vn"}	null	\N	\N	\N	{"\\"useDefault\\""}	{"dateTime": "2020-11-08T02:30:00-01:00"}	confirmed	Lời nhắc: Bạn có lớp học diễn ra với Bệ Phóng Việt Nam Digital 4.0	\N	2021-02-27 01:40:06.161	\N
10339	2qr1a9rkk5g82t30rob6nfdauf_20220523T233000Z	\N	\N	\N	\N	null	null	null	\N	\N	null	\N	\N	\N	\N	\N	\N	\N	null	{"dateTime": "2022-05-23T23:30:00Z", "timeZone": "Asia/Ho_Chi_Minh"}	\N	\N	\N	\N	null	cancelled	\N	\N	\N	\N
10371	rnra5dohtbd2brj7q9dd5s3tik_20220624T030329Z	\N	\N	\N	\N	null	null	null	\N	\N	null	\N	\N	\N	\N	\N	\N	\N	null	{"dateTime": "2022-06-24T03:03:29Z", "timeZone": "Atlantic/Azores"}	\N	\N	\N	\N	null	cancelled	\N	\N	\N	\N
10382	hta0v5itm23pes30183i0nt7qs_20220624T033729Z	\N	\N	\N	\N	null	null	null	\N	\N	null	\N	\N	\N	\N	\N	\N	\N	null	{"dateTime": "2022-06-24T03:37:29Z", "timeZone": "Atlantic/Azores"}	\N	\N	\N	\N	null	cancelled	\N	\N	\N	\N
10386	crbap16o80k2cl1r7m5fb9eakc	\N	\N	What:\nCuộc họp 30 phút\n  \n\nInvitee Time Zone:\nAsia/Bangkok\n  \n\nWho:\n\nCal Project - Organizer\ncal.uetunited@gmail.com\n  \nDo Xuan Cuong\ndoxuancuong1996@gmail.com\n      \nDo Xuan Cuong 2\ndoxuancuong96@gmail.com\n      \n  \nWhere:\nhttps://app.cal.com/video/gdxgbDS72NqYh3aHrFwMgA\n\n\n\n\nNeed to reschedule or cancel?\nhttps://app.cal.com/cancel/gdxgbDS72NqYh3aHrFwMgA	\N	null	{"email": "cal.uetunited@gmail.com"}	{"dateTime": "2022-06-27T02:30:00Z", "timeZone": "Asia/Bangkok"}	\N	default	null	\N	\N	\N	https://www.google.com/calendar/event?eid=Y3JiYXAxNm84MGsyY2wxcjdtNWZiOWVha2MgZG94dWFuY3Vvbmc5NkBt	crbap16o80k2cl1r7m5fb9eakc@google.com	https://app.cal.com/video/gdxgbDS72NqYh3aHrFwMgA	\N	{"email": "cal.uetunited@gmail.com"}	null	\N	\N	\N	{"\\"useDefault\\""}	{"dateTime": "2022-06-27T02:00:00Z", "timeZone": "Asia/Bangkok"}	confirmed	Cuộc họp 30 phút between Cal Project and Do Xuan Cuong	\N	2022-06-24 10:00:58.968	\N
10387	njf34diokd8cogf4bilmrn3bao	\N	\N	What:\nCuộc họp 30 phút\n  \n\nInvitee Time Zone:\nAsia/Bangkok\n  \n\nWho:\n\nCal Project - Organizer\ncal.uetunited@gmail.com\n  \nDo Xuan Cuong\ndoxuancuong1996@gmail.com\n      \nGuest\ndoxuancuong96@gmail.com\n      \n  \nWhere:\nDaily\n\n\n\n\nNeed to reschedule or cancel?\nhttps://app.cal.com/cancel/jyozWJhbf8HMoaXaaxZCiP	\N	null	{"email": "cal.uetunited@gmail.com"}	{"dateTime": "2022-06-28T02:30:00Z", "timeZone": "Asia/Bangkok"}	\N	default	null	\N	\N	\N	https://www.google.com/calendar/event?eid=bmpmMzRkaW9rZDhjb2dmNGJpbG1ybjNiYW8gZG94dWFuY3Vvbmc5NkBt	njf34diokd8cogf4bilmrn3bao@google.com	Daily	\N	{"email": "cal.uetunited@gmail.com"}	null	\N	\N	\N	{"\\"useDefault\\""}	{"dateTime": "2022-06-28T02:00:00Z", "timeZone": "Asia/Bangkok"}	confirmed	Cuộc họp 30 phút between Cal Project and Do Xuan Cuong	\N	2022-06-24 10:04:04.721	\N
10388	24r2dmbel1no9m1l8e8uoafoe0	\N	\N	\N	\N	{"entryPoints": [{"entryPointType": "video", "uri": "https://meet.google.com/jwe-mxpo-goh", "label": "meet.google.com/jwe-mxpo-goh"}], "conferenceSolution": {"key": {"type": "hangoutsMeet"}, "name": "Google Meet", "iconUri": "https://fonts.gstatic.com/s/i/productlogos/meet_2020q4/v6/web-512dp/logo_meet_2020q4_color_2x_web_512dp.png"}, "conferenceId": "jwe-mxpo-goh"}	{"email": "dungvv.vnu@gmail.com"}	{"dateTime": "2022-06-30T09:30:00Z", "timeZone": "Asia/Ho_Chi_Minh"}	\N	default	null	\N	\N	\N	https://www.google.com/calendar/event?eid=MjRyMmRtYmVsMW5vOW0xbDhlOHVvYWZvZTAgZG94dWFuY3Vvbmc5NkBt	24r2dmbel1no9m1l8e8uoafoe0@google.com	\N	\N	{"email": "dungvv.vnu@gmail.com"}	null	\N	\N	\N	{"\\"useDefault\\""}	{"dateTime": "2022-06-30T08:30:00Z", "timeZone": "Asia/Ho_Chi_Minh"}	confirmed	ahuhu	\N	2022-06-30 08:23:06.794	\N
10390	4blgt2ml94m3k31c5949rrueir	\N	\N	\N	\N	{"entryPoints": [{"entryPointType": "video", "uri": "https://meet.google.com/ptf-kzdq-csz", "label": "meet.google.com/ptf-kzdq-csz"}], "conferenceSolution": {"key": {"type": "hangoutsMeet"}, "name": "Google Meet", "iconUri": "https://fonts.gstatic.com/s/i/productlogos/meet_2020q4/v6/web-512dp/logo_meet_2020q4_color_2x_web_512dp.png"}, "conferenceId": "ptf-kzdq-csz"}	{"email": "doxuancuong1996@gmail.com"}	{"dateTime": "2022-06-28T11:30:00Z", "timeZone": "Asia/Ho_Chi_Minh"}	\N	default	null	\N	\N	\N	https://www.google.com/calendar/event?eid=NGJsZ3QybWw5NG0zazMxYzU5NDlycnVlaXIgZG94dWFuY3Vvbmc5NkBt	4blgt2ml94m3k31c5949rrueir@google.com	Hanoi, Hoàn Kiếm, Hanoi, Vietnam	\N	{"email": "doxuancuong1996@gmail.com"}	null	\N	\N	\N	{"\\"useDefault\\""}	{"dateTime": "2022-06-28T10:30:00Z", "timeZone": "Asia/Ho_Chi_Minh"}	confirmed	test event 3	\N	2022-07-01 03:28:16.965	\N
\.


--
-- TOC entry 3063 (class 0 OID 35778)
-- Dependencies: 207
-- Data for Name: profile; Type: TABLE DATA; Schema: public; Owner: lcp39
--

COPY public.profile (id, account_id, full_name, avatar, description, language, timezone, time_format, first_day_of_week) FROM stdin;
10001	10003	\N	Avatar		EN	UTC	HH	SU
10002	10005	\N	\N	\N	\N	\N	\N	\N
10003	10006	Cương Đỗ Xuân	https://lh3.googleusercontent.com/a-/AOh14GhESsNHEqvI2pgUhqTudqGFCi7Etp_w3nM8DxqR=s96-c		EN	UTC	HH	SU
10004	10007	Cương Đỗ Xuân	https://lh3.googleusercontent.com/a-/AOh14Gh5VdGZJbvT9A93U2vgPV6pAYESDEzUd3cGJ02oLg=s96-c		EN	UTC	HH	SU
\.


--
-- TOC entry 3083 (class 0 OID 0)
-- Dependencies: 204
-- Name: account_id_seq; Type: SEQUENCE SET; Schema: public; Owner: lcp39
--

SELECT pg_catalog.setval('public.account_id_seq', 10007, true);


--
-- TOC entry 3084 (class 0 OID 0)
-- Dependencies: 211
-- Name: calendar_id_seq; Type: SEQUENCE SET; Schema: public; Owner: lcp39
--

SELECT pg_catalog.setval('public.calendar_id_seq', 10110, true);


--
-- TOC entry 3085 (class 0 OID 0)
-- Dependencies: 208
-- Name: connection_id_seq; Type: SEQUENCE SET; Schema: public; Owner: lcp39
--

SELECT pg_catalog.setval('public.connection_id_seq', 10009, true);


--
-- TOC entry 3086 (class 0 OID 0)
-- Dependencies: 214
-- Name: event_id_seq; Type: SEQUENCE SET; Schema: public; Owner: lcp39
--

SELECT pg_catalog.setval('public.event_id_seq', 10432, true);


--
-- TOC entry 3087 (class 0 OID 0)
-- Dependencies: 206
-- Name: profile_id_seq; Type: SEQUENCE SET; Schema: public; Owner: lcp39
--

SELECT pg_catalog.setval('public.profile_id_seq', 10004, true);


--
-- TOC entry 2914 (class 2606 OID 43972)
-- Name: account_connection account_connection_pkey; Type: CONSTRAINT; Schema: public; Owner: lcp39
--

ALTER TABLE ONLY public.account_connection
    ADD CONSTRAINT account_connection_pkey PRIMARY KEY (account_id, connection_id);


--
-- TOC entry 2908 (class 2606 OID 35775)
-- Name: account account_pkey; Type: CONSTRAINT; Schema: public; Owner: lcp39
--

ALTER TABLE ONLY public.account
    ADD CONSTRAINT account_pkey PRIMARY KEY (id);


--
-- TOC entry 2922 (class 2606 OID 44102)
-- Name: calendar_event calendar_event_pkey; Type: CONSTRAINT; Schema: public; Owner: lcp39
--

ALTER TABLE ONLY public.calendar_event
    ADD CONSTRAINT calendar_event_pkey PRIMARY KEY (calendar_id, event_id);


--
-- TOC entry 2916 (class 2606 OID 43993)
-- Name: calendar calendar_pkey; Type: CONSTRAINT; Schema: public; Owner: lcp39
--

ALTER TABLE ONLY public.calendar
    ADD CONSTRAINT calendar_pkey PRIMARY KEY (id);


--
-- TOC entry 2918 (class 2606 OID 44001)
-- Name: connection_calendar connection_calendar_pkey; Type: CONSTRAINT; Schema: public; Owner: lcp39
--

ALTER TABLE ONLY public.connection_calendar
    ADD CONSTRAINT connection_calendar_pkey PRIMARY KEY (connection_id, calendar_id);


--
-- TOC entry 2912 (class 2606 OID 43957)
-- Name: connection connection_pkey; Type: CONSTRAINT; Schema: public; Owner: lcp39
--

ALTER TABLE ONLY public.connection
    ADD CONSTRAINT connection_pkey PRIMARY KEY (id);


--
-- TOC entry 2920 (class 2606 OID 44022)
-- Name: event event_pkey; Type: CONSTRAINT; Schema: public; Owner: lcp39
--

ALTER TABLE ONLY public.event
    ADD CONSTRAINT event_pkey PRIMARY KEY (id);


--
-- TOC entry 2910 (class 2606 OID 35786)
-- Name: profile profile_pkey; Type: CONSTRAINT; Schema: public; Owner: lcp39
--

ALTER TABLE ONLY public.profile
    ADD CONSTRAINT profile_pkey PRIMARY KEY (id);


--
-- TOC entry 2924 (class 2606 OID 43973)
-- Name: account_connection account_connection_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lcp39
--

ALTER TABLE ONLY public.account_connection
    ADD CONSTRAINT account_connection_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.account(id);


--
-- TOC entry 2925 (class 2606 OID 43978)
-- Name: account_connection account_connection_connection_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lcp39
--

ALTER TABLE ONLY public.account_connection
    ADD CONSTRAINT account_connection_connection_id_fkey FOREIGN KEY (connection_id) REFERENCES public.connection(id);


--
-- TOC entry 2928 (class 2606 OID 44103)
-- Name: calendar_event calendar_event_calendar_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lcp39
--

ALTER TABLE ONLY public.calendar_event
    ADD CONSTRAINT calendar_event_calendar_id_fkey FOREIGN KEY (calendar_id) REFERENCES public.calendar(id);


--
-- TOC entry 2929 (class 2606 OID 44108)
-- Name: calendar_event calendar_event_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lcp39
--

ALTER TABLE ONLY public.calendar_event
    ADD CONSTRAINT calendar_event_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.event(id);


--
-- TOC entry 2927 (class 2606 OID 44007)
-- Name: connection_calendar connection_calendar_calendar_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lcp39
--

ALTER TABLE ONLY public.connection_calendar
    ADD CONSTRAINT connection_calendar_calendar_id_fkey FOREIGN KEY (calendar_id) REFERENCES public.calendar(id);


--
-- TOC entry 2926 (class 2606 OID 44002)
-- Name: connection_calendar connection_calendar_connection_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lcp39
--

ALTER TABLE ONLY public.connection_calendar
    ADD CONSTRAINT connection_calendar_connection_id_fkey FOREIGN KEY (connection_id) REFERENCES public.connection(id);


--
-- TOC entry 2923 (class 2606 OID 35787)
-- Name: profile profile_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lcp39
--

ALTER TABLE ONLY public.profile
    ADD CONSTRAINT profile_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.account(id);


-- Completed on 2022-07-01 15:30:31

--
-- PostgreSQL database dump complete
--

