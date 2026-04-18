--
-- PostgreSQL database dump
--

\restrict dtLTMAU6h5VnVTm4eweJmOplGiFUti93dv9bDTi7VATvx9o1DQpSDvaLSLrXM1r

-- Dumped from database version 14.22 (Ubuntu 14.22-0ubuntu0.22.04.1)
-- Dumped by pg_dump version 14.22 (Ubuntu 14.22-0ubuntu0.22.04.1)

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
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: device_tokens; Type: TABLE; Schema: public; Owner: fauxpg
--

CREATE TABLE public.device_tokens (
    id integer NOT NULL,
    user_id uuid,
    token text NOT NULL,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.device_tokens OWNER TO fauxpg;

--
-- Name: device_tokens_id_seq; Type: SEQUENCE; Schema: public; Owner: fauxpg
--

CREATE SEQUENCE public.device_tokens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.device_tokens_id_seq OWNER TO fauxpg;

--
-- Name: device_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: fauxpg
--

ALTER SEQUENCE public.device_tokens_id_seq OWNED BY public.device_tokens.id;


--
-- Name: devices; Type: TABLE; Schema: public; Owner: fauxpg
--

CREATE TABLE public.devices (
    chip_id character varying(100) NOT NULL,
    user_id uuid NOT NULL,
    name character varying(100) NOT NULL,
    status character varying(50) DEFAULT 'offline'::character varying,
    last_seen timestamp with time zone DEFAULT now() NOT NULL,
    api_key character varying(255) NOT NULL
);


ALTER TABLE public.devices OWNER TO fauxpg;

--
-- Name: medlogs; Type: TABLE; Schema: public; Owner: fauxpg
--

CREATE TABLE public.medlogs (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    user_id uuid NOT NULL,
    device_id character varying(100) NOT NULL,
    pillname character varying(100) NOT NULL,
    scheduled_time timestamp without time zone DEFAULT now() NOT NULL,
    status character varying(50) NOT NULL
);


ALTER TABLE public.medlogs OWNER TO fauxpg;

--
-- Name: notifications; Type: TABLE; Schema: public; Owner: fauxpg
--

CREATE TABLE public.notifications (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    device_id character varying(100) NOT NULL,
    user_id uuid NOT NULL,
    message character varying(255) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.notifications OWNER TO fauxpg;

--
-- Name: schedules; Type: TABLE; Schema: public; Owner: fauxpg
--

CREATE TABLE public.schedules (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    user_id uuid NOT NULL,
    device_id character varying(100) NOT NULL,
    pillname character varying(100) NOT NULL,
    dose_time time without time zone NOT NULL,
    repeat_days integer DEFAULT 0
);


ALTER TABLE public.schedules OWNER TO fauxpg;

--
-- Name: users; Type: TABLE; Schema: public; Owner: fauxpg
--

CREATE TABLE public.users (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying(100) NOT NULL,
    email character varying(100) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role character varying(50) DEFAULT 'patient'::character varying NOT NULL
);


ALTER TABLE public.users OWNER TO fauxpg;

--
-- Name: wifi_configs; Type: TABLE; Schema: public; Owner: fauxpg
--

CREATE TABLE public.wifi_configs (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    user_id uuid NOT NULL,
    device_id character varying NOT NULL,
    ssid character varying NOT NULL,
    password character varying NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.wifi_configs OWNER TO fauxpg;

--
-- Name: device_tokens id; Type: DEFAULT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.device_tokens ALTER COLUMN id SET DEFAULT nextval('public.device_tokens_id_seq'::regclass);


--
-- Data for Name: device_tokens; Type: TABLE DATA; Schema: public; Owner: fauxpg
--

COPY public.device_tokens (id, user_id, token, created_at) FROM stdin;
\.


--
-- Data for Name: devices; Type: TABLE DATA; Schema: public; Owner: fauxpg
--

COPY public.devices (chip_id, user_id, name, status, last_seen, api_key) FROM stdin;
00DE3855B594	fd1ff641-ec8a-4424-9c1f-4b5c1f2c91e6	SAP04	offline	2026-04-19 06:45:50.728122+07	71d3880b72db1e18f23cec342897fb155b25de1876990f08e6e1c173a53ef754
F0B5AD286F24	fd1ff641-ec8a-4424-9c1f-4b5c1f2c91e6	SAP03	offline	2026-04-19 06:45:41.367051+07	08f5d1f653b0b65ef3b4600e74890fcc06b1130733023142e0658ee9a338bb8c
F4A2B6B24354	fd1ff641-ec8a-4424-9c1f-4b5c1f2c91e6	SAP01	offline	2026-04-19 06:45:27.211085+07	7cc30933c7b4ad980886fda2e58f1e01539d30620449bd05e742c6c1d2fffd04
C87BC4286F24	fd1ff641-ec8a-4424-9c1f-4b5c1f2c91e6	SAP02	offline	2026-02-12 23:00:32.743838+07	b6d1c1cda37e9e8bd4d3730d8a20f51882c5f97075b2cdc18c683f320a3172bb
\.


--
-- Data for Name: medlogs; Type: TABLE DATA; Schema: public; Owner: fauxpg
--

COPY public.medlogs (id, user_id, device_id, pillname, scheduled_time, status) FROM stdin;
\.


--
-- Data for Name: notifications; Type: TABLE DATA; Schema: public; Owner: fauxpg
--

COPY public.notifications (id, device_id, user_id, message, created_at) FROM stdin;
\.


--
-- Data for Name: schedules; Type: TABLE DATA; Schema: public; Owner: fauxpg
--

COPY public.schedules (id, user_id, device_id, pillname, dose_time, repeat_days) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: fauxpg
--

COPY public.users (id, name, email, password_hash, role) FROM stdin;
fd1ff641-ec8a-4424-9c1f-4b5c1f2c91e6	Caretaker	caretaker@gmail.com	$argon2id$v=19$m=65536,t=3,p=4$7L1XyjnHeM/Zm/M+J4TwPg$qe71LEgKzTFASqW58KwF/CCfja/o3tNcQmEP+I65rvc	caretaker
a87b9694-fdc7-44be-97fd-ce46ec172736	Patient	patient@gmail.com	$argon2id$v=19$m=65536,t=3,p=4$B6A0ZgzBeO/d+19LCYEQwg$AzcpYGrH4LQr4BAnFoCzs5afkNrtIWpZY3NCwDBSxYA	patient
\.


--
-- Data for Name: wifi_configs; Type: TABLE DATA; Schema: public; Owner: fauxpg
--

COPY public.wifi_configs (id, user_id, device_id, ssid, password, created_at) FROM stdin;
276fc2c9-11ef-4b3a-8aec-652003b6d004	fd1ff641-ec8a-4424-9c1f-4b5c1f2c91e6	C87BC4286F24	string	gAAAAABppEsEs46nZzmaUO2GmwAYg4mfacf7-_tpRB_sORUxWidMsfm7vwWBATmR8AeEbmxOjWquwQv43cNS8cj5_nR3Gml00A==	2026-03-01 21:19:48.361
\.


--
-- Name: device_tokens_id_seq; Type: SEQUENCE SET; Schema: public; Owner: fauxpg
--

SELECT pg_catalog.setval('public.device_tokens_id_seq', 1, false);


--
-- Name: device_tokens device_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.device_tokens
    ADD CONSTRAINT device_tokens_pkey PRIMARY KEY (id);


--
-- Name: devices devices_pkey; Type: CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.devices
    ADD CONSTRAINT devices_pkey PRIMARY KEY (chip_id);


--
-- Name: medlogs medlogs_pkey; Type: CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.medlogs
    ADD CONSTRAINT medlogs_pkey PRIMARY KEY (id);


--
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);


--
-- Name: schedules schedules_pkey; Type: CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.schedules
    ADD CONSTRAINT schedules_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: wifi_configs wifi_configs_pkey; Type: CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.wifi_configs
    ADD CONSTRAINT wifi_configs_pkey PRIMARY KEY (id);


--
-- Name: device_tokens device_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.device_tokens
    ADD CONSTRAINT device_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: devices devices_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.devices
    ADD CONSTRAINT devices_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: medlogs medlogs_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.medlogs
    ADD CONSTRAINT medlogs_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.devices(chip_id);


--
-- Name: medlogs medlogs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.medlogs
    ADD CONSTRAINT medlogs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: notifications notifications_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.devices(chip_id);


--
-- Name: notifications notifications_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: schedules schedules_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.schedules
    ADD CONSTRAINT schedules_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.devices(chip_id);


--
-- Name: schedules schedules_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.schedules
    ADD CONSTRAINT schedules_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: wifi_configs wifi_configs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.wifi_configs
    ADD CONSTRAINT wifi_configs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

\unrestrict dtLTMAU6h5VnVTm4eweJmOplGiFUti93dv9bDTi7VATvx9o1DQpSDvaLSLrXM1r

