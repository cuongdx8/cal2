--
-- PostgreSQL database dump
--

-- Dumped from database version 13.5 (Ubuntu 13.5-0ubuntu0.21.04.1)
-- Dumped by pg_dump version 14.3

-- Started on 2022-07-06 15:59:45

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
-- TOC entry 240 (class 1255 OID 44630)
-- Name: delete_calendar_by_connection_ids(integer, integer[]); Type: PROCEDURE; Schema: public; Owner: lcp39
--

CREATE PROCEDURE public.delete_calendar_by_connection_ids(cal_id integer, con_ids integer[])
    LANGUAGE plpgsql
    AS $$
declare
    is_exists_connect_with_calendar int;
    event_remove_list int[];
begin
    delete from connection_calendar cc where cc.connection_id = any(con_ids) and cc.calendar_id = cal_id;
    is_exists_connect_with_calendar = (select count(1) from connection_calendar cc where cc.calendar_id = cal_id);
    if is_exists_connect_with_calendar = 0 then
        -- find all event only in this calendar
        event_remove_list = ARRAY(
            select cal.event_id event_id from calendar_event cal
            where cal.calendar_id = cal_id
            group by cal.event_id
            having count(cal.event_id) = 1
        );

        -- remove all calendar_event with calendar_id = cal_id
        delete from calendar_event where calendar_id = cal_id;

        -- remove all event only in this calendar
        delete from event where event.id = any(event_remove_list);

        -- remove calendar;
        delete from calendar where id = cal_id;

    end if;
end;
$$;


ALTER PROCEDURE public.delete_calendar_by_connection_ids(cal_id integer, con_ids integer[]) OWNER TO lcp39;

--
-- TOC entry 241 (class 1255 OID 44059)
-- Name: disconnect_connection(integer, integer); Type: PROCEDURE; Schema: public; Owner: lcp39
--

CREATE PROCEDURE public.disconnect_connection(con_id integer, acc_id integer)
    LANGUAGE plpgsql
    AS $$
declare
    check_exists_relationship int;
    count_result int;
    element_id int;
    calendar_removed int[];
begin
    check_exists_relationship = (select count(1) from account_connection where account_id = acc_id and connection_id = con_id);
    if check_exists_relationship > 0 then
        delete from account_connection where account_id = acc_id and connection_id = con_id;
        count_result = (select count(account_id) from account_connection where connection_id = con_id);
        if count_result = 0 then
            calendar_removed = ARRAY(
                select calendar_id from connection_calendar
                where calendar_id in (
                    select calendar_id from connection_calendar where connection_id = con_id
                )
                group by calendar_id having count(calendar_id) = 1
            );
            FOREACH element_id IN ARRAY calendar_removed LOOP
              call delete_calendar_by_connection_ids(element_id, ARRAY[con_id]);
            END LOOP ;
            delete from connection where id = con_id;
        end if;
    else
        raise exception 'Not found relationship between account_id and connection_id: %, %', con_id, acc_id
            using hint = 'Please check your account_id and connection_id';
    end if;

end;$$;


ALTER PROCEDURE public.disconnect_connection(con_id integer, acc_id integer) OWNER TO lcp39;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 217 (class 1259 OID 35767)
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
-- TOC entry 222 (class 1259 OID 43968)
-- Name: account_connection; Type: TABLE; Schema: public; Owner: lcp39
--

CREATE TABLE public.account_connection (
    account_id integer NOT NULL,
    connection_id integer NOT NULL
);


ALTER TABLE public.account_connection OWNER TO lcp39;

--
-- TOC entry 216 (class 1259 OID 35765)
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
-- TOC entry 3077 (class 0 OID 0)
-- Dependencies: 216
-- Name: account_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lcp39
--

ALTER SEQUENCE public.account_id_seq OWNED BY public.account.id;


--
-- TOC entry 224 (class 1259 OID 43985)
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
-- TOC entry 228 (class 1259 OID 44095)
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
-- TOC entry 223 (class 1259 OID 43983)
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
-- TOC entry 3078 (class 0 OID 0)
-- Dependencies: 223
-- Name: calendar_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lcp39
--

ALTER SEQUENCE public.calendar_id_seq OWNED BY public.calendar.id;


--
-- TOC entry 221 (class 1259 OID 43949)
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
-- TOC entry 225 (class 1259 OID 43994)
-- Name: connection_calendar; Type: TABLE; Schema: public; Owner: lcp39
--

CREATE TABLE public.connection_calendar (
    connection_id integer NOT NULL,
    calendar_id integer NOT NULL,
    access_role character varying,
    default_flag boolean,
    owner_flag boolean
);


ALTER TABLE public.connection_calendar OWNER TO lcp39;

--
-- TOC entry 220 (class 1259 OID 43947)
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
-- TOC entry 3079 (class 0 OID 0)
-- Dependencies: 220
-- Name: connection_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lcp39
--

ALTER SEQUENCE public.connection_id_seq OWNED BY public.connection.id;


--
-- TOC entry 227 (class 1259 OID 44014)
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
-- TOC entry 226 (class 1259 OID 44012)
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
-- TOC entry 3080 (class 0 OID 0)
-- Dependencies: 226
-- Name: event_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lcp39
--

ALTER SEQUENCE public.event_id_seq OWNED BY public.event.id;


--
-- TOC entry 219 (class 1259 OID 35778)
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
-- TOC entry 218 (class 1259 OID 35776)
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
-- TOC entry 3081 (class 0 OID 0)
-- Dependencies: 218
-- Name: profile_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lcp39
--

ALTER SEQUENCE public.profile_id_seq OWNED BY public.profile.id;


--
-- TOC entry 2914 (class 2604 OID 35770)
-- Name: account id; Type: DEFAULT; Schema: public; Owner: lcp39
--

ALTER TABLE ONLY public.account ALTER COLUMN id SET DEFAULT nextval('public.account_id_seq'::regclass);


--
-- TOC entry 2917 (class 2604 OID 43988)
-- Name: calendar id; Type: DEFAULT; Schema: public; Owner: lcp39
--

ALTER TABLE ONLY public.calendar ALTER COLUMN id SET DEFAULT nextval('public.calendar_id_seq'::regclass);


--
-- TOC entry 2916 (class 2604 OID 43952)
-- Name: connection id; Type: DEFAULT; Schema: public; Owner: lcp39
--

ALTER TABLE ONLY public.connection ALTER COLUMN id SET DEFAULT nextval('public.connection_id_seq'::regclass);


--
-- TOC entry 2918 (class 2604 OID 44017)
-- Name: event id; Type: DEFAULT; Schema: public; Owner: lcp39
--

ALTER TABLE ONLY public.event ALTER COLUMN id SET DEFAULT nextval('public.event_id_seq'::regclass);


--
-- TOC entry 2915 (class 2604 OID 35781)
-- Name: profile id; Type: DEFAULT; Schema: public; Owner: lcp39
--

ALTER TABLE ONLY public.profile ALTER COLUMN id SET DEFAULT nextval('public.profile_id_seq'::regclass);


--
-- TOC entry 2926 (class 2606 OID 43972)
-- Name: account_connection account_connection_pkey; Type: CONSTRAINT; Schema: public; Owner: lcp39
--

ALTER TABLE ONLY public.account_connection
    ADD CONSTRAINT account_connection_pkey PRIMARY KEY (account_id, connection_id);


--
-- TOC entry 2920 (class 2606 OID 35775)
-- Name: account account_pkey; Type: CONSTRAINT; Schema: public; Owner: lcp39
--

ALTER TABLE ONLY public.account
    ADD CONSTRAINT account_pkey PRIMARY KEY (id);


--
-- TOC entry 2934 (class 2606 OID 44102)
-- Name: calendar_event calendar_event_pkey; Type: CONSTRAINT; Schema: public; Owner: lcp39
--

ALTER TABLE ONLY public.calendar_event
    ADD CONSTRAINT calendar_event_pkey PRIMARY KEY (calendar_id, event_id);


--
-- TOC entry 2928 (class 2606 OID 43993)
-- Name: calendar calendar_pkey; Type: CONSTRAINT; Schema: public; Owner: lcp39
--

ALTER TABLE ONLY public.calendar
    ADD CONSTRAINT calendar_pkey PRIMARY KEY (id);


--
-- TOC entry 2930 (class 2606 OID 44001)
-- Name: connection_calendar connection_calendar_pkey; Type: CONSTRAINT; Schema: public; Owner: lcp39
--

ALTER TABLE ONLY public.connection_calendar
    ADD CONSTRAINT connection_calendar_pkey PRIMARY KEY (connection_id, calendar_id);


--
-- TOC entry 2924 (class 2606 OID 43957)
-- Name: connection connection_pkey; Type: CONSTRAINT; Schema: public; Owner: lcp39
--

ALTER TABLE ONLY public.connection
    ADD CONSTRAINT connection_pkey PRIMARY KEY (id);


--
-- TOC entry 2932 (class 2606 OID 44022)
-- Name: event event_pkey; Type: CONSTRAINT; Schema: public; Owner: lcp39
--

ALTER TABLE ONLY public.event
    ADD CONSTRAINT event_pkey PRIMARY KEY (id);


--
-- TOC entry 2922 (class 2606 OID 35786)
-- Name: profile profile_pkey; Type: CONSTRAINT; Schema: public; Owner: lcp39
--

ALTER TABLE ONLY public.profile
    ADD CONSTRAINT profile_pkey PRIMARY KEY (id);


--
-- TOC entry 2936 (class 2606 OID 43973)
-- Name: account_connection account_connection_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lcp39
--

ALTER TABLE ONLY public.account_connection
    ADD CONSTRAINT account_connection_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.account(id);


--
-- TOC entry 2937 (class 2606 OID 43978)
-- Name: account_connection account_connection_connection_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lcp39
--

ALTER TABLE ONLY public.account_connection
    ADD CONSTRAINT account_connection_connection_id_fkey FOREIGN KEY (connection_id) REFERENCES public.connection(id);


--
-- TOC entry 2940 (class 2606 OID 44103)
-- Name: calendar_event calendar_event_calendar_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lcp39
--

ALTER TABLE ONLY public.calendar_event
    ADD CONSTRAINT calendar_event_calendar_id_fkey FOREIGN KEY (calendar_id) REFERENCES public.calendar(id);


--
-- TOC entry 2941 (class 2606 OID 44108)
-- Name: calendar_event calendar_event_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lcp39
--

ALTER TABLE ONLY public.calendar_event
    ADD CONSTRAINT calendar_event_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.event(id);


--
-- TOC entry 2939 (class 2606 OID 44007)
-- Name: connection_calendar connection_calendar_calendar_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lcp39
--

ALTER TABLE ONLY public.connection_calendar
    ADD CONSTRAINT connection_calendar_calendar_id_fkey FOREIGN KEY (calendar_id) REFERENCES public.calendar(id);


--
-- TOC entry 2938 (class 2606 OID 44002)
-- Name: connection_calendar connection_calendar_connection_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lcp39
--

ALTER TABLE ONLY public.connection_calendar
    ADD CONSTRAINT connection_calendar_connection_id_fkey FOREIGN KEY (connection_id) REFERENCES public.connection(id);


--
-- TOC entry 2935 (class 2606 OID 35787)
-- Name: profile profile_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lcp39
--

ALTER TABLE ONLY public.profile
    ADD CONSTRAINT profile_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.account(id);


-- Completed on 2022-07-06 15:59:55

--
-- PostgreSQL database dump complete
--

